import pytest
from unittest.mock import patch, MagicMock

from aws_handler.sqs import AwsHelper  
from exceptions.sqs_exceptions import SQSMessageBatchNotSent

@pytest.fixture
def mock_queue():
    m = MagicMock()
    m.send_message.return_value = {'SequenceNumber': '1234567890'}
    m.send_messages.return_value = {'Successful': []}
    return m

@pytest.fixture
def patch_boto3_resource(mock_queue):
    with patch('aws_handler.sqs.boto3.resource') as mock_resource:
        mock_resource.return_value.Queue.return_value = mock_queue
        yield

@pytest.fixture
def mock_sqs_client():
    with patch("boto3.client") as mock_client:
        yield mock_client

@pytest.fixture
def mock_sqs_resource():
    with patch("boto3.resource") as mock_resource:
        yield mock_resource

@pytest.fixture
def aws_helper(mock_sqs_resource, mock_sqs_client, mock_queue):
    # Mock queue object on boto3.resource
    mock_sqs_resource.return_value.Queue.return_value = mock_queue
    mock_sqs_client.return_value = MagicMock()

    helper = AwsHelper(queue_url="https://queue.amazonaws.com/123/test-queue", fallback_queue_url="https://queue.amazonaws.com/123/fb")
    helper._QUEUE = mock_queue   # ensure queue is mocked
    helper._SQS = mock_sqs_client.return_value  # ensure SQS client is mocked
    helper._FALLBACK_QUEUE = mock_queue
    return helper

def test_send_message_success_fails_without_url(patch_boto3_resource, mock_queue):
    with pytest.raises(TypeError):
        AwsHelper()

def test_send_message_success(aws_helper, mock_queue):
    aws = aws_helper
    aws.send_message("Breaking news: AI beats chess grandmaster.")
    mock_queue.send_message.assert_called_once_with(
        MessageBody="Breaking news: AI beats chess grandmaster.",
        MessageGroupId='headlines'
    )

def test_send_message_exception(aws_helper, capsys, mock_queue):
    mock_queue.send_message.side_effect = Exception("SQS error")
    aws = aws_helper
    aws.send_message("Will not send")
    captured = capsys.readouterr()
    assert "Message could not be sent: SQS error" in captured.out

def test_send_batch_single_batch(aws_helper):
    aws = aws_helper
    headlines = [f"headline {i}" for i in range(10)]
    aws.send_batch(headlines, 'headlines')
    assert aws._SQS.send_message_batch.call_count == 1
    args, kwargs = aws._SQS.send_message_batch.call_args
    entries = kwargs['Entries']
    assert len(entries) == 10
    for i, entry in enumerate(entries):
        assert entry['Id'] == str(i)
        assert entry['MessageGroupId'] == 'headlines'
        assert entry['MessageBody'] == f"headline {i}"

def test_send_batch_multiple_batches(aws_helper):
    aws = aws_helper
    headlines = [f"headline {i}" for i in range(25)]
    aws.send_batch(headlines)
    # Should be 3 batches: 10, 10, and 5
    assert aws._SQS.send_message_batch.call_count == 3
    batch_sizes = [call.kwargs['Entries'] for call in aws._SQS.send_message_batch.call_args_list]
    assert [len(b) for b in batch_sizes] == [10, 10, 5]

def test_send_batch_exception_prints_error(aws_helper, capsys, caplog):
    aws = aws_helper
    aws._SQS.send_message_batch.side_effect = [Exception("Batch error"), None]
    headlines = [f"headline {i}" for i in range(11)]
    with pytest.raises(SQSMessageBatchNotSent):
         aws.send_batch(headlines)

    assert "Batch 0 could not be sent." in caplog.text

def test_delete_message_success(aws_helper):
    aws_helper._SQS = MagicMock()
    aws_helper.delete_message_main_queue("abc123")
    aws_helper._SQS.delete_message.assert_called_once()


def test_delete_message_invalid_receipt(aws_helper):
    with pytest.raises(ValueError):
        aws_helper.delete_message_main_queue("")


def test_delete_messages_batch_success(aws_helper):
    aws_helper._SQS = MagicMock()
    msgs = [
        {"MessageId": "1", "ReceiptHandle": "rh1"},
        {"MessageId": "2", "ReceiptHandle": "rh2"}
    ]
    aws_helper.delete_messages_batch(msgs, "https://queue.amazonaws.com/123/fb")
    aws_helper._SQS.delete_message_batch.assert_called_once()
    # Check that correct entries were formed
    entries = aws_helper._SQS.delete_message_batch.call_args[1]["Entries"]
    assert entries[0]["Id"] == "1"


def test_delete_messages_batch_no_messages(aws_helper):
    # Should do nothing
    aws_helper._SQS = MagicMock()
    aws_helper.delete_messages_batch([], "https://queue.amazonaws.com/123/fb")
    aws_helper._SQS.delete_message_batch.assert_not_called()


def test_send_to_fallback_no_url(aws_helper, capsys):
    aws_helper.fallback_queue_url = None
    aws_helper._FALLBACK_QUEUE= None 
    with pytest.raises(Exception, match="Fallback queue not provided for this instance."):
        aws_helper.send_messages_to_fallback_queue([{"Body": "test", "ReceiptHandle": "Test"}])


def test_send_to_fallback_success(aws_helper):
    msgs = [{"Body": "msg1", "ReceiptHandle": "r1"}]
    aws_helper.send_messages_to_fallback_queue(msgs)
    aws_helper._SQS.send_message_batch.assert_called_once()
    aws_helper._SQS.delete_message_batch.assert_called_once()  

def test_send_to_fallback_batch_handling(aws_helper):
    msgs = [{"Body": f"msg{i}", "ReceiptHandle": "r1"} for i in range(15)]
    aws_helper.send_messages_to_fallback_queue(msgs)
    assert aws_helper._SQS.send_message_batch.call_count == 2