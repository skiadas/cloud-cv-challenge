import boto3
import json
import os

## SAM part
def lambda_incoming_to_sqs_handler(event, context):
  request = event['Records'][0]['cf']['request']
  process_incoming_request(request, os.environ['QUEUE_NAME'])

  return request

def lambda_processing_sqs_message(event, context):
  request = event['Records'][0]['body']
  process_sqs_message(body)

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

def process_sqs_message(body):
  d = json.loads(body)
  dynamodb = boto3.client('dynamodb')
  dynamodb.update_item(
    TableName=os.environ['SITE_COUNTS'],
    Key={'path': { 'S': d['path'] }},
    UpdateExpression='ADD #c :n',
    ExpressionAttributeNames={'#c': 'count'},
    ExpressionAttributeValues={':n': { 'N': '1' }})
