import boto3
import os

def lambda_incoming_to_sqs_handler(event, context):
  request = event['Records'][0]['cf']['request']
  incomingQueue = os.environ['QUEUE_NAME']

  sqs = boto3.client('sqs')
  sqs.send_message(
    QueueUrl=incomingQueue,
    MessageBody="message"
  )
  return request
