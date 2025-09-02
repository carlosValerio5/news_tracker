import boto3
from datetime import datetime

'''sqs handler module containing bussiness logic for publishing and consuming sqs'''
class AwsHelper():

    '''Publisher class to send headlines to sqs'''

    def __init__(self):
        self.__SQS = boto3.resource('sqs')
        self.__QUEUE = self.__SQS.get_queue_by_name(QueueName='news_queue.fifo')


    '''Send a single message'''
    def send_message(self, headline: str):
        try:
            response = self.__QUEUE.send_message(MessageBody=headline, MessageGroupId='headlines')
            print(response['SequenceNumber'])
        except Exception as e:
            print(f"Message could not be sent: {e}")

    '''Send messages in batches of 10'''
    def send_batch(self, headlines: list):
        batch= []
        for i in range(len(headlines)):
            item = {}
            item['Id'] = str(i)
            item['MessageBody'] = headlines[i]
            item['MessageGroupId'] = 'headlines'
            batch.append(item)
            
            if len(batch) == 10:
                try:
                    self.__QUEUE.send_messages(Entries=batch)
                except Exception as e:
                    print(f"Batch {i//10} could not be sent: {e}")
                batch = []

        if batch:
            try:
                self.__QUEUE.send_messages(Entries=batch)
            except Exception as e:
                print(f"Batch {i//10} could not be sent: {e}")
