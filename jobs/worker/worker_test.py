import pytest
import json
from unittest.mock import patch, MagicMock

import types
import logging

import builtins

from jobs.worker.worker import HeadlineProcessService, WorkerJob, GoogleTrendsService
# replace `jobs.worker.worker` with the actual module filename

# ---------------------
# Fixtures
# ---------------------

@pytest.fixture
def mock_nlp():
    """
    Returns a fake spacy nlp function that yields fake tokens
    """
    Token = lambda text, lemma_, pos_, is_alpha: types.SimpleNamespace(
        text=text, lemma_=lemma_, pos_=pos_, is_alpha=is_alpha
    )
    # 3 tokens, PROPN, NOUN, ADJ
    doc = [
        Token("Apple", "Apple", "PROPN", True),
        Token("phone", "phone", "NOUN", True),
        Token("great", "great", "ADJ", True)
    ]
    return lambda text: doc


@pytest.fixture
def patch_spacy_load(mock_nlp):
    with patch("jobs.worker.nlp_service.spacy.load") as mock_load:
        mock_load.return_value = mock_nlp
        yield


@pytest.fixture
def mock_processor_service(patch_spacy_load):
    return HeadlineProcessService()


@pytest.fixture
def mock_aws_handler():
    aws = MagicMock()
    return aws


@pytest.fixture
def mock_session_factory():
    return MagicMock()

@pytest.fixture
def worker_with_mocks(mock_processor_service, mock_aws_handler, mock_session_factory):
    """Return a WorkerJob instance with mocked API and processor_service."""
    processor_service = mock_processor_service
    api = MagicMock()
    aws_handler = mock_aws_handler 
    session_factory = mock_session_factory 
    worker = WorkerJob(api, processor_service, aws_handler, session_factory)
    return worker, processor_service, api

# ---------------------
# WorkerJob tests
# ---------------------

def test_process_messages_happy_path(mock_processor_service, mock_aws_handler, mock_session_factory):
    # Fake a headline message
    msgs = [{"Body": json.dumps({"id": 1, "headline": "Breaking news"}), "ReceiptHandle": "abc123"}]
    mock_aws_handler.poll_messages.return_value = msgs
    mock_aws_handler.delete_message_main_queue.return_value = None

    mock_processor_service.extract_keywords = MagicMock(return_value={"keyword_1": "Apple"})

    write_batch_returning_value = [{
        "id" : 1,
        "keyword_1": "Apple",
        "keyword_2": None,
        "keyword_3": None,
        "composed_query" :"Apple"
    }]

    with patch("jobs.worker.worker.DataBaseHelper.write_batch_of_objects", return_value=True) as mock_write, \
        patch("jobs.worker.worker.DataBaseHelper.write_batch_of_objects_and_return", return_value=write_batch_returning_value) as mock_write_returning:

        mock_aws_handler.poll_messages.return_value = [
            {"Body": json.dumps({"id": 1, "headline": "Breaking news"}), "ReceiptHandle": "abc123"}
        ]
        mock_aws_handler.delete_message_main_queue.return_value = None

        job = WorkerJob(MagicMock(), mock_processor_service, mock_aws_handler, mock_session_factory)
        job._processor_service.get_principal_keyword = MagicMock(return_value='Apple')

        job.estimate_popularity = MagicMock(return_value=[{
            'article_keywords_id': 1,
            'has_data': True,
            'peak_interest': 100,
            'current_interest': 20,
            'data_period_start': '2025-09-12',
            'data_period_end': '2025-09-12'
        }])
        job.process_messages()
        mock_write.assert_called_once()
        mock_write_returning.assert_called_once()
        mock_processor_service.extract_keywords.assert_called_once()


def test_process_messages_no_messages(mock_processor_service, mock_aws_handler, mock_session_factory, caplog):
    mock_aws_handler.poll_messages.return_value = []
    job = WorkerJob(MagicMock(), mock_processor_service, mock_aws_handler, mock_session_factory)
    with caplog.at_level(logging.WARNING):
        job.process_messages()
    assert "No keywords extracted" in caplog.text

def test_process_messages_poll_exception(mock_processor_service, mock_aws_handler, mock_session_factory):
    mock_aws_handler.poll_messages.side_effect = Exception("poll fail")
    job = WorkerJob(MagicMock(), mock_processor_service, mock_aws_handler, mock_session_factory)
    with pytest.raises(Exception):
        job.process_messages()

def test_process_list_of_messages_with_blank_body(mock_processor_service, mock_aws_handler, mock_session_factory):
    mock_aws_handler.send_message_to_fallback_queue = MagicMock()
    messages = [{"Body": " ", "ReceiptHandle": "abc"}]  # blank string headline
    job = WorkerJob(MagicMock(), mock_processor_service, mock_aws_handler, mock_session_factory)
    results = job.process_list_of_messages(messages)
    assert results == []
    mock_aws_handler.send_message_to_fallback_queue.assert_called_once()

def test_process_list_of_messages_with_extraction_failure(mock_processor_service, mock_aws_handler, mock_session_factory):
    mock_aws_handler.send_message_to_fallback_queue = MagicMock()
    mock_processor_service.extract_keywords = MagicMock(side_effect=Exception("fail extraction"))
    messages = [{"Body": "valid", "ReceiptHandle": "abc"}]
    job = WorkerJob(MagicMock(), mock_processor_service, mock_aws_handler, mock_session_factory)
    results = job.process_list_of_messages(messages)
    assert results == []
    mock_aws_handler.send_message_to_fallback_queue.assert_called_once()

def test_process_list_of_messages_success_delete_error(mock_processor_service, mock_aws_handler, mock_session_factory):
    mock_processor_service.extract_keywords = MagicMock(return_value={"keyword_1": "Apple"})
    mock_aws_handler.delete_message_main_queue = MagicMock(side_effect=ValueError("bad receipt"))
    mock_aws_handler.send_message_to_fallback_queue = MagicMock()
    messages = [{"Body": json.dumps({"id": 1, "headline": "valid"}), "ReceiptHandle": "abc"}]
    job = WorkerJob(MagicMock(), mock_processor_service, mock_aws_handler, mock_session_factory)
    results = job.process_list_of_messages(messages)
    assert len(results) == 1
    mock_aws_handler.send_message_to_fallback_queue.assert_called_once()

def test_estimate_popularity_happy_path(worker_with_mocks):
    worker, processor_service, api = worker_with_mocks
    # Mocks
    processor_service.get_principal_keyword = MagicMock(return_value="Apple")
    api.estimate_popularity.return_value = {"has_data": True}

    result_input = [
        {"id": 1, "keyword_1": "Apple", "keyword_2": None, "keyword_3": None}
    ]

    output = worker.estimate_popularity(result_input)

    processor_service.get_principal_keyword.assert_called_once_with(["Apple", None, None])
    api.estimate_popularity.assert_called_once_with("Apple")

    # The id is used as a key in the returned dict per current implementation
    assert output == [{"has_data": True, 'article_keywords_id': 1}]


def test_estimate_popularity_skips_when_api_returns_falsy(worker_with_mocks, caplog):
    worker, processor_service, api = worker_with_mocks
    processor_service.get_principal_keyword = MagicMock(return_value = "Apple")
    api.estimate_popularity.return_value = {}  # falsy

    result_input = [
        {"id": 5, "keyword_1": "Apple", "keyword_2": None, "keyword_3": None}
    ]

    with caplog.at_level("ERROR"):
        output = worker.estimate_popularity(result_input)

    assert output == []  # Should skip appending
    assert "Failed to estimate popularity for keywords with id 5" in caplog.text


def test_estimate_popularity_multiple_rows(worker_with_mocks):
    worker, processor_service, api = worker_with_mocks
    processor_service.get_principal_keyword = MagicMock(side_effect=["Apple", "Banana"])
    api.estimate_popularity.side_effect = [
        {"has_data": True}, 
        {"has_data": True}
    ]

    result_input = [
        {"id": 1, "keyword_1": "Apple", "keyword_2": None, "keyword_3": None},
        {"id": 2, "keyword_1": "Banana", "keyword_2": "Yellow", "keyword_3": None},
    ]

    output = worker.estimate_popularity(result_input)

    assert len(output) == 2
    # Check that ids got added as keys into the returned dicts (current logic)
    assert all(entry['article_keywords_id'] in [1, 2] for entry in output)
    assert processor_service.get_principal_keyword.call_count == 2
    assert api.estimate_popularity.call_count == 2