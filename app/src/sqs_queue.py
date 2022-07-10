from boto3 import client

## Manages a queue with a given name. Right now quite error-prone,
# for starters it always creates the queue, so used mostly for testing
# and with a moto-mocked sqs
class sqs_queue:
    def __init__(self, queueName, regionName='us-east-1'):
        self.url = None
        self.sqs = client('sqs', region_name=regionName)
        self.queueName = queueName
        self.sqs.create_queue(QueueName=self.queueName)

    def get_url(self):
        if self.url == None:
            # Should add some more error-checking here
            self.url = self.sqs.get_queue_url(
                QueueName=self.queueName)['QueueUrl']
        return self.url

    def get_attribute(self, attribute):
        return self.sqs.get_queue_attributes(
            QueueUrl=self.get_url(),
            AttributeNames=[attribute]
        )['Attributes'][attribute]

    def get_next_message_body(self):
        return self.get_next_message()['Body']

    def get_next_message(self):
        return self.sqs.receive_message(
            QueueUrl=self.get_url(),
            MaxNumberOfMessages=1)['Messages'][0]
