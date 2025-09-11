import pytest
from unittest.mock import patch, MagicMock
import types
from types import SimpleNamespace

from jobs.worker.worker import HeadlineProcessService, WorkerJob, GoogleTrendsService

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

@pytest.fixture
def service():
    return HeadlineProcessService()

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
    processor_service.get_level_of_confidence = lambda pos, idx: 2.5
    processor_service._nlp = lambda text: [
        types.SimpleNamespace(lemma_="apple", pos_="PROPN", is_alpha=True),
        types.SimpleNamespace(lemma_="banana", pos_="NOUN", is_alpha=True),
    ]
    result = processor_service.process_headline("fake text")
    assert isinstance(result, list)
    assert all(isinstance(kw[0], str) for kw in result)



# ----------
# _get_total_confidence
# ----------
def test_get_total_confidence_rounds_result(service):
    keywords = [("apple", 1.234), ("banana", 2.345)]
    result = service._get_total_confidence(keywords)
    # 1.234 + 2.345 = 3.579 → round to 3.58
    assert result == 3.58


# ----------
# get_level_of_confidence
# ----------
@pytest.mark.parametrize("pos, index, expected", [
    ("PROPN", 0, 2.0 + 1/1),  # PROPN is 2.0 + 1.0
    ("NOUN", 1, 1.5 + 1/2),   # NOUN is 1.5 + 0.5
    ("ADJ", 2, 1.0 + 1/3),    # ADJ is 1.0 + 0.333...
])
def test_get_level_of_confidence(service, pos, index, expected):
    result = service.get_level_of_confidence(pos, index)
    assert result == pytest.approx(expected)


# ----------
# process_headline
# ----------
def test_process_headline_filters_and_sorts(service):
    # Fake tokens → token.pos_ must match service.POS_WEIGHTS keys for inclusion
    Token = lambda lemma, pos, is_alpha=True: SimpleNamespace(
        lemma_=lemma, pos_=pos, is_alpha=is_alpha
    )

    # Return in order: one that will score higher, one lower
    fake_doc = [
        Token("apple", "PROPN"),    # High score 2.0 + 1.0
        Token("banana", "NOUN"),    # Lower score 1.5 + 0.5
        Token("apple", "PROPN"),    # Duplicate lemma, should be skipped
        Token("great", "ADJ"),      # 1.0 + pos_weight
    ]

    service._nlp = MagicMock(return_value=fake_doc)
    service.get_level_of_confidence = MagicMock(side_effect=lambda pos, idx: {
        ("PROPN", 0): 3.0,
        ("NOUN", 1): 2.0,
        ("ADJ", 3): 1.1
    }[(pos, idx)])

    results = service.process_headline("any text", max_keywords=2)
    # Should return top 2 keywords sorted by score
    assert results == [("Apple", 3.0), ("Banana", 2.0)]


def test_process_headline_empty_doc(service):
    service._nlp = MagicMock(return_value=[])
    results = service.process_headline("anything")
    assert results == []


# ----------
# get_principal_keyword
# ----------
def test_get_principal_keyword_picks_highest_score(service):
    # Fake ents objects
    Ent = lambda text, label: SimpleNamespace(text=text, label_=label)
    # Fake doc with ents
    fake_doc = SimpleNamespace(
        ents=[
            Ent("Apple", "ORG"),   # Suppose LABEL_WEIGHTS["ORG"] exists
            Ent("Banana", "PERSON")
        ]
    )
    service._nlp = MagicMock(return_value=fake_doc)
    # Assume default LABEL_WEIGHTS exists
    service.LABEL_WEIGHTS = {"ORG": 2.0, "PERSON": 1.5}

    result = service.get_principal_keyword(["Apple", "Banana"])
    assert result == "Apple"  # ORG first with highest label_score


def test_get_principal_keyword_no_matching_labels(service):
    Ent = lambda text, label: SimpleNamespace(text=text, label_=label)
    fake_doc = SimpleNamespace(
        ents=[
            Ent("Apple", "UNKNOWN"),
            Ent("Banana", "ALSO_UNKNOWN")
        ]
    )
    service._nlp = MagicMock(return_value=fake_doc)
    service.LABEL_WEIGHTS = {"ORG": 2.0}  # No matches

    result = service.get_principal_keyword(["Apple", "Banana"])
    assert result == ""  # Default empty string returned