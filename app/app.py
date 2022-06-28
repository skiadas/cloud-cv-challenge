import boto3
import json
import os

## SAM part
def lambda_incoming_to_sqs_handler(event, context):
  request = event['Records'][0]['cf']['request']
  process_incoming_request(request, os.environ['QUEUE_NAME'])

  return request

## Unit-testable parts

def process_incoming_request(request, incomingQueue):
  message = json.dumps({
    "ip": request['clientIp'],
    "path": request['uri']
  })
  send_to_queue(incomingQueue, message)

def send_to_queue(queue, message):
  sqs = boto3.client('sqs')
  sqs.send_message(QueueUrl=queue, MessageBody=message)
