import pytest
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
    with patch("jobs.worker.worker.spacy.load") as mock_load:
        mock_load.return_value = mock_nlp
        yield


@pytest.fixture
def processor_service(patch_spacy_load):
    return HeadlineProcessService()


@pytest.fixture
def mock_aws_handler():
    aws = MagicMock()
    return aws


@pytest.fixture
def mock_session_factory():
    return MagicMock()


# ---------------------
# HeadlineProcessService tests
# ---------------------

def test_extract_keywords_returns_expected_fields(processor_service):
    with patch.object(processor_service, "process_headline", return_value=[("Test", 1.5), ("Item", 1.0)]) as mock_proc:
        result = processor_service.extract_keywords("Some headline")
        assert result["keyword_1"] == "Test"
        assert result["keyword_2"] == "Item"
        assert result["keyword_3"] is None
        assert isinstance(result["extraction_confidence"], float)
        mock_proc.assert_called_once()

def test_extract_keywords_raises_on_fail(processor_service):
    with patch.object(processor_service, "process_headline", side_effect=Exception("fail proc")):
        with pytest.raises(Exception) as e:
            processor_service.extract_keywords("headline")
        assert "Failed to process headline" in str(e.value)

def test__get_total_confidence(processor_service):
    keywords = [("word", 1.0), ("another", 2.0)]
    assert processor_service._get_total_confidence(keywords) == 3.0

def test_get_level_of_confidence_scores_correctly(processor_service):
    score = processor_service.get_level_of_confidence("PROPN", 0)
    assert pytest.approx(score) == 2.0 + 1.0  # POS=2.0 + position_score=1

def test_process_headline_extracts_keywords(processor_service):
    # monkeypatch get_level_of_confidence to avoid POS mismatch in lemma arg
    def fake_conf(*args, **kwargs):
        return 2.5
    processor_service.get_level_of_confidence = lambda kw, pos, idx: 2.5
    processor_service._nlp = lambda text: [
        types.SimpleNamespace(lemma_="apple", pos_="PROPN", is_alpha=True),
        types.SimpleNamespace(lemma_="banana", pos_="NOUN", is_alpha=True),
    ]
    result = processor_service.process_headline("fake text")
    assert isinstance(result, list)
    assert all(isinstance(kw[0], str) for kw in result)


# ---------------------
# WorkerJob tests
# ---------------------

def test_process_messages_happy_path(processor_service, mock_aws_handler, mock_session_factory):
    # Fake a headline message
    msgs = [{"Body": "Breaking News", "ReceiptHandle": "abc123"}]
    mock_aws_handler.poll_messages.return_value = msgs
    mock_aws_handler.delete_message_main_queue.return_value = None

    processor_service.extract_keywords = MagicMock(return_value={"keyword_1": "Apple"})

    with patch("jobs.worker.worker.DataBaseHelper.write_batch_of_objects", return_value=True) as mock_write:
        job = WorkerJob(MagicMock(), processor_service, mock_aws_handler, mock_session_factory)
        job.process_messages()
        mock_write.assert_called_once()
        processor_service.extract_keywords.assert_called_once()


def test_process_messages_no_messages(processor_service, mock_aws_handler, mock_session_factory, caplog):
    mock_aws_handler.poll_messages.return_value = []
    job = WorkerJob(MagicMock(), processor_service, mock_aws_handler, mock_session_factory)
    with caplog.at_level(logging.WARNING):
        job.process_messages()
    assert "No keywords extracted" in caplog.text

def test_process_messages_poll_exception(processor_service, mock_aws_handler, mock_session_factory):
    mock_aws_handler.poll_messages.side_effect = Exception("poll fail")
    job = WorkerJob(MagicMock(), processor_service, mock_aws_handler, mock_session_factory)
    with pytest.raises(Exception):
        job.process_messages()

def test_process_list_of_messages_with_blank_body(processor_service, mock_aws_handler, mock_session_factory):
    mock_aws_handler.send_message_to_fallback_queue = MagicMock()
    messages = [{"Body": " ", "ReceiptHandle": "abc"}]  # blank string headline
    job = WorkerJob(MagicMock(), processor_service, mock_aws_handler, mock_session_factory)
    results = job.process_list_of_messages(messages)
    assert results == []
    mock_aws_handler.send_message_to_fallback_queue.assert_called_once()

def test_process_list_of_messages_with_extraction_failure(processor_service, mock_aws_handler, mock_session_factory):
    mock_aws_handler.send_message_to_fallback_queue = MagicMock()
    processor_service.extract_keywords = MagicMock(side_effect=Exception("fail extraction"))
    messages = [{"Body": "valid", "ReceiptHandle": "abc"}]
    job = WorkerJob(MagicMock(), processor_service, mock_aws_handler, mock_session_factory)
    results = job.process_list_of_messages(messages)
    assert results == []
    mock_aws_handler.send_message_to_fallback_queue.assert_called_once()

def test_process_list_of_messages_success_delete_error(processor_service, mock_aws_handler, mock_session_factory):
    processor_service.extract_keywords = MagicMock(return_value={"keyword_1": "Apple"})
    mock_aws_handler.delete_message_main_queue = MagicMock(side_effect=ValueError("bad receipt"))
    mock_aws_handler.send_message_to_fallback_queue = MagicMock()
    messages = [{"Body": "valid", "ReceiptHandle": "abc"}]
    job = WorkerJob(MagicMock(), processor_service, mock_aws_handler, mock_session_factory)
    results = job.process_list_of_messages(messages)
    assert len(results) == 1
    mock_aws_handler.send_message_to_fallback_queue.assert_called_once()