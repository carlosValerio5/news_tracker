'''Defines exceptions to handle sqs related errors.'''

class NoSQSFoundException(Exception):
    '''Thrown when sqs service could not be found'''
    pass

class SQSMessageBatchNotSent(Exception):
    '''Exception thrown when a batch of messages could not be sent to sqs queue.'''
    pass