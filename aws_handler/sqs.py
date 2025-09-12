import boto3
import json
from datetime import datetime
import logging
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

'''sqs handler module containing bussiness logic for publishing and consuming sqs'''
class AwsHelper:
    """Publisher/helper class for SQS work and fallback handling."""

    def __init__(self, queue_url: str, region_name: str = 'us-east-2', fallback_queue_url: str = None):
        """
        Initialize an SQS client.

        :param queue_url: The full URL of the main SQS queue
        :param region_name: AWS region where the queue resides
        :param fallback_queue_url: The full URL of the fallback SQS queue (optional)
        """
        if not queue_url:
            raise ValueError("queue_url is required")
        self.queue_url = queue_url
        self.fallback_queue_url = fallback_queue_url
        self._SQS = self._get_service()

        try:
            # This gets the actual Queue resource for high-level send calls
            self._QUEUE = boto3.resource('sqs', region_name=region_name).Queue(queue_url)
        except Exception as e:
            logger.exception(f'Failed to get queue resource: {e}')
            raise

        if fallback_queue_url:
            try:
                self._FALLBACK_QUEUE = boto3.resource('sqs', region_name=region_name).Queue(queue_url)
            except Exception as e:
                logger.exception(f'Failed to get fallback queue resource: {e}')
                raise
        

    def _get_service(self):
        '''Get SQS queue'''

        try:
            client  = boto3.client('sqs')
        except Exception as e:
            print(f'Failed to retrieve service: {e}')

        return client


    def send_message(self, headline: str):
        '''
        Send a single message
        
        :param headline: The headline of the news article 
        '''

        try:
            response = self._QUEUE.send_message(MessageBody=headline, MessageGroupId='headlines')
            print(response['SequenceNumber'])
        except Exception as e:
            print(f"Message could not be sent: {e}")

    def send_batch(self, headlines: list):
        '''
        Send messages in batches of 10\
           
        :param headline: list containing all headlines
        '''

        batch= []
        for i in range(len(headlines)):
            item = {}
            item['Id'] = str(i)
            item['MessageBody'] = headlines[i]
            item['MessageGroupId'] = 'headlines'
            batch.append(item)
            
            if len(batch) == 10:
                try:
                    self._QUEUE.send_messages(Entries=batch)
                except Exception as e:
                    print(f"Batch {i//10} could not be sent: {e}")
                batch = []

        if batch:
            try:
                self._QUEUE.send_messages(Entries=batch)
            except Exception as e:
                print(f"Batch {i//10} could not be sent: {e}")

    def poll_messages(self,max_messages: int = 10, wait_time: int = 10,visibility_timeout: int = 30) -> list[dict]:
        """
        Poll messages from the SQS queue using long polling.

        :param max_messages: Max number of messages (1–10) to fetch per call
        :param wait_time: Long polling wait time in seconds (0–20)
        :param visibility_timeout: How long the message remains invisible to others (seconds)
        :return: List of messages (each is a dict with Body, MessageId, ReceiptHandle, etc.)
        """

        try:
            response = self._SQS.receive_message(
                QueueUrl = self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time,
                VisibilityTimeout=visibility_timeout
            )
            messages = response.get("Messages", [])
            if messages:
                logger.info("Fetched %d messages from SQS", len(messages))
            else:
                logger.info("No messages available in the SQS queue.")
            
            return messages
        
        except (BotoCoreError, ClientError) as e:
            logger.exception("Error polling SQS queue: %s", e)
            return []
        
    
    def delete_message_main_queue(self, receipt_handle: str):
        """
        Delete a single message from the SQS main queue.
        
        :param receipt_handle: The SQS receipt handle from the message
        """

        if not receipt_handle:
            raise ValueError('Wrong format for receipt handle.')

        try:
            self._SQS.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            logger.info("Deleted message from SQS.")
        except (BotoCoreError, ClientError) as e:
            logger.exception("Error deleting SQS message: %s", e)

    def delete_message_fallback_queue(self, receipt_handle: str):
        """
        Delete a single message from the SQS fallback queue.

        :param receipt_handle: The SQS receipt handle from the message
        """

        if not receipt_handle:
            raise ValueError('Wrong format for receipt handle.')

        try:
            self._FALLBACK_QUEUE.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            logger.info("Deleted message from SQS.")
        except (BotoCoreError, ClientError) as e:
            logger.exception("Error deleting SQS message: %s", e)
    
    def delete_messages_batch(self, messages: list, queue_url: str):
        """
        Delete a batch of messages from main SQS queue.

        :param messages: List of messages as returned by receive_message
        :param queue_url: URL of the target queue.
        """
        if not queue_url:
            raise ValueError("queue_url required")

        if not messages:
            return

        entries = [
            {"Id": msg.get('Id') or msg.get('MessageId'), "ReceiptHandle": msg["ReceiptHandle"]}
            for msg in messages
        ]
        try:
            resp = self._SQS.delete_message_batch(
                QueueUrl=queue_url,
                Entries=entries
            )
            if "Failed" in resp and resp["Failed"]:
                logger.warning("Failed to delete some messages: %s", resp["Failed"])
            else:
                logger.info("Deleted %d messages from SQS.", len(entries))
        except (BotoCoreError, ClientError) as e:
            logger.exception("Error in batch delete from SQS: %s", e)

    def send_messages_to_fallback_queue(self, messages: list):
        """
        Send failed messages to the fallback SQS queue.

        :param messages: List of failed messages (each dict must have 'Body' or 'MessageBody')
        """
        if not self._FALLBACK_QUEUE:
            raise Exception("Fallback queue not provided for this instance.")

        # Send in batches of 10
        batch = []
        for i, msg in enumerate(messages):
            body = msg.get("Body") or msg.get("MessageBody", "")
            receipt_handle = msg.get('ReceiptHandle')
            batch.append({
                'Id': str(i),
                'MessageBody': body,
                'MessageGroupId': 'fallback',
                'ReceiptHandle' : receipt_handle 
            })

            if len(batch) == 10:
                self._send_fallback_batch(self._FALLBACK_QUEUE, batch)
                batch = []
                self.delete_messages_batch(batch, self.fallback_queue_url)

        if batch:
            self._send_fallback_batch(self._FALLBACK_QUEUE, batch)
            self.delete_messages_batch(batch, self.fallback_queue_url)

    def send_message_to_fallback_queue(self, message: dict):
        '''
        Sends a single message to the fallback queue

        :param message: dict object containing the message.
        '''
        if not message:
            raise ValueError('Message empty')
        
        body = json.dumps(message)
        receipt_handle = message.get('ReceiptHandle')

        if not receipt_handle:
            raise ValueError('No receipt handle in this message.')
        
        try:
            self._SQS.send_message(QueueUrl=self.fallback_queue_url, MessageBody=body)
        except ClientError:
            raise

        try:
            self.delete_message_fallback_queue(receipt_handle)
        except ValueError:
            raise 
        except (BotoCoreError, ClientError):
            raise

    def _send_fallback_batch(self, fallback_queue, batch):
        '''
        Sends batches of maximum length 10 messages to the fallback queue

        :param fallback_queue: the target queue to send messages to.
        '''
        try:
            fallback_queue.send_messages(Entries=batch)
            logger.info(f"Fallback batch of {len(batch)} messages sent.")
        except Exception as e:
            logger.exception(f"Failed to send fallback batch: {e}")