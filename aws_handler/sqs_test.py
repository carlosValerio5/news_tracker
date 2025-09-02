import pytest
from unittest.mock import patch, MagicMock

from aws_handler.sqs import AwsHelper  # update this line to match your actual module name

@pytest.fixture
def mock_queue():
    m = MagicMock()
    m.send_message.return_value = {'SequenceNumber': '1234567890'}
    m.send_messages.return_value = {'Successful': []}
    return m

@pytest.fixture
def patch_boto3_resource(mock_queue):
    with patch('aws_handler.sqs.boto3.resource') as mock_resource:
        mock_resource.return_value.get_queue_by_name.return_value = mock_queue
        yield

def test_send_message_success(patch_boto3_resource, mock_queue):
    aws = AwsHelper()
    aws.send_message("Breaking news: AI beats chess grandmaster.")
    mock_queue.send_message.assert_called_once_with(MessageBody="Breaking news: AI beats chess grandmaster.", MessageGroupId='headlines')

def test_send_message_exception(patch_boto3_resource, mock_queue, capsys):
    mock_queue.send_message.side_effect = Exception("SQS error")
    aws = AwsHelper()
    aws.send_message("Will not send")
    captured = capsys.readouterr()
    assert "Message could not be sent: SQS error" in captured.out

def test_send_batch_single_batch(patch_boto3_resource, mock_queue):
    aws = AwsHelper()
    headlines = [f"headline {i}" for i in range(10)]
    aws.send_batch(headlines)
    assert mock_queue.send_messages.call_count == 1
    args, kwargs = mock_queue.send_messages.call_args
    entries = kwargs['Entries']
    assert len(entries) == 10
    for i, entry in enumerate(entries):
        assert entry['Id'] == str(i)
        assert entry['MessageGroupId'] == 'headlines'
        assert entry['MessageBody'] == f"headline {i}"

def test_send_batch_multiple_batches(patch_boto3_resource, mock_queue):
    aws = AwsHelper()
    headlines = [f"headline {i}" for i in range(25)]
    aws.send_batch(headlines)
    # Should be 3 batches: 10, 10, and 5
    assert mock_queue.send_messages.call_count == 3
    batch_sizes = [call.kwargs['Entries'] for call in mock_queue.send_messages.call_args_list]
    assert [len(b) for b in batch_sizes] == [10, 10, 5]

def test_send_batch_exception_prints_error(patch_boto3_resource, mock_queue, capsys):
    aws = AwsHelper()
    mock_queue.send_messages.side_effect = [Exception("Batch error"), None]
    headlines = [f"headline {i}" for i in range(11)]
    aws.send_batch(headlines)
    captured = capsys.readouterr()
    assert "Batch 0 could not be sent: Batch error" in captured.out