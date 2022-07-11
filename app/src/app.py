import boto3
import json
import os
from dynamodb import dbtable

BUCKET_PREFIX = os.getenv('BUCKET_PREFIX', '/skiadas/resume/counters')
QUEUE_PARAMETER = BUCKET_PREFIX + '/request_queue_name'
TOTALS_TABLE_PARAMETER = BUCKET_PREFIX + '/totals_table_name'
PATHS_TABLE_PARAMETER = BUCKET_PREFIX + '/paths_table_name'
IPS_TABLE_PARAMETER = BUCKET_PREFIX + '/ips_table_name'
AWS_REGION = 'us-east-1'

## SAM part
def lambda_incoming_to_sqs_handler(event, context):
  request = event['Records'][0]['cf']['request']
  queueName = retrieveQueueName()
  process_incoming_request(request, queueName)

  return request

def lambda_processing_sqs_message(event, context):
  body = event['Records'][0]['body']
  process_sqs_message(body)

def lambda_read_db_data(event, context):
  query = event['queryStringParameters']
  count_data = read_db_data(query)
  return {
      statusCode: 200,
      body: JSON.stringify(count_data)
  }

def retrieveQueueName():
  if 'QUEUE_NAME' in os.environ:
    return os.environ['QUEUE_NAME']
  return get_ssm_parameter(QUEUE_PARAMETER)

## Unit-testable parts

def process_incoming_request(request, incomingQueue):
  message = json.dumps({
    "ip": request['clientIp'],
    "path": request['uri']
  })
  send_to_queue(incomingQueue, message)

def send_to_queue(queue, message):
  sqs = boto3.client('sqs', region_name=AWS_REGION)
  sqs.send_message(QueueUrl=queue, MessageBody=message)

def process_sqs_message(body):
  d = json.loads(body)
  dbtable(get_paths_table_name(), 'path').increaseCount(d['path'])
  dbtable(get_ips_table_name(), 'ip').increaseCount(d['ip'])
  dbtable(get_totals_table_name(), 'total').increaseCount('total')

def read_db_data(query):
  return {
      'ip': dbtable(get_ips_table_name(), 'ip').get(query['ip']),
      'path': dbtable(get_paths_table_name(), 'path').get(query['path']),
      'total': dbtable(get_totals_table_name(), 'total').get('total')
  }


def get_db_value(tableName, keyName):
    boto3.client('dynamodb').get_item(
        TableName=tableName,
        Key={keyName: {'S': keyValue}},
        UpdateExpression='ADD #c :n',
        ExpressionAttributeNames={'#c': 'count'},
        ExpressionAttributeValues={':n': {'N': '1'}})

def get_ssm_parameter(parameterName):
  ssm = boto3.client('ssm', region_name=AWS_REGION)
  return ssm.get_parameter(
      Name=parameterName,
      WithDecryption=False)['Parameter']['Value']

def get_totals_table_name():
  if 'TOTAL_COUNT' in os.environ:
    return os.environ['TOTAL_COUNT']
  return get_ssm_parameter(TOTALS_TABLE_PARAMETER)

def get_ips_table_name():
  if 'IP_COUNTS' in os.environ:
    return os.environ['IP_COUNTS']
  return get_ssm_parameter(IPS_TABLE_PARAMETER)

def get_paths_table_name():
  if 'SITE_COUNTS' in os.environ:
    return os.environ['SITE_COUNTS']
  return get_ssm_parameter(PATHS_TABLE_PARAMETER)
