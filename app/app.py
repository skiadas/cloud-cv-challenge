import boto3
import json
import os
from dynamodb import dbtable

## SAM part
def lambda_incoming_to_sqs_handler(event, context):
  request = event['Records'][0]['cf']['request']
  process_incoming_request(request, os.environ['QUEUE_NAME'])

  return request

def lambda_processing_sqs_message(event, context):
  body = event['Records'][0]['body']
  process_sqs_message(body)

def lambda_read_db_data(event, context):
  query = event['queryStringParameters']
  data = read_db_data(query)
  return {
      statusCode: 200,
      body: JSON.stringify(data)
  }

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
  dbtable(os.environ['SITE_COUNTS'], 'path').increaseCount(d['path'])
  dbtable(os.environ['IP_COUNTS'], 'ip').increaseCount(d['ip'])
  dbtable(os.environ['TOTAL_COUNT'], 'total').increaseCount('total')

def read_db_data(query):
  path = query['path']
  ip = query['ip']


def get_db_value(tableName, keyName):
    boto3.client('dynamodb').get_item(
        TableName=tableName,
        Key={keyName: {'S': keyValue}},
        UpdateExpression='ADD #c :n',
        ExpressionAttributeNames={'#c': 'count'},
        ExpressionAttributeValues={':n': {'N': '1'}})
