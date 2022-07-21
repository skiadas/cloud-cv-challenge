import boto3
import json
import os
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlencode

from dynamodb import dbtable

PROD_BUCKET = '/skiadas/resume/counters'
DEV_BUCKET = '/dev-skiadas/resume/counters'
DATE_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
SESSIONID_NAME = 'SKIADAS_RESUME_SESSION'
BUCKET_PREFIX = os.getenv('BUCKET_PREFIX', PROD_BUCKET)
QUEUE_PARAMETER = '/request_queue_name'
TOTALS_TABLE_PARAMETER = '/totals_table_name'
PATHS_TABLE_PARAMETER = '/paths_table_name'
IPS_TABLE_PARAMETER = '/ips_table_name'
AWS_REGION = 'us-east-1'

## SAM part

def lambda_incoming_to_sqs_handler(event, context):
  return lambda_incoming_to_sqs_handler_inner(event, context, '/skiadas/resume/counters')

# Version of the handler for a live dev version
# Needed because we cannot alter the bucket otherwise
def lambda_incoming_to_sqs_handler_dev(event, context):
  return lambda_incoming_to_sqs_handler_inner(event, context, '/dev-skiadas/resume/counters')

def lambda_incoming_to_sqs_handler_inner(event, context, bucketPrefix):
  request = event['Records'][0]['cf']['request']
  # currentSession = get_current_session_id(request)
  # if currentSession is None:
  #   return redirect_with_new_session(request)
  queueName = retrieveQueueName(bucketPrefix)
  process_incoming_request(request, queueName)

  return request

def lambda_processing_sqs_message(event, context):
  body = event['Records'][0]['body']
  process_sqs_message(body)

def lambda_read_db_data(event, context):
  query = event['queryStringParameters']
  count_data = read_db_data(query)
  return {
      'statusCode': 200,
      'body': JSON.stringify(count_data)
  }

def retrieveQueueName(bucketPrefix):
  if 'QUEUE_NAME' in os.environ:
    return os.environ['QUEUE_NAME']
  return get_ssm_parameter(QUEUE_PARAMETER, bucketPrefix)

## Unit-testable parts

def redirect_with_new_session(request):
  return {
    "statusCode": 302,
    'headers': {
      'location': {
        'value': 'https://' + request['headers']['host'] +
                              request['uri'] +
                              encode_query_string(request['querystring'])
      }
    },
    "cookies": {
      SESSIONID_NAME: {
        "value": generate_session_id(),
        "attributes": "Expires=" + expire_date(2 * 60)
      }
    }
  }

def generate_session_id():
  return secrets.token_urlsafe(16)

def expire_date(minutesFromNow):
  return DATE_FORMAT.format(datetime.now() + timedelta(minutes=minutesFromNow))

def encode_query_string(q_obj):
  tuples = [(k, _get_query_values(v)) for k, v in q_obj.items()]
  return "?" + urlencode(tuples, doseq=True)

def _get_query_values(v):
  if 'multiValue' in v:
    return [x['value'] for x in v['multiValue']]
  return v['value']

def get_current_session_id(request):
    cookies = request['cookies']
    if SESSIONID_NAME in cookies:
      return cookies[SESSIONID_NAME]['value']
    return None

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

def get_ssm_parameter(parameterName, bucketPrefix=PROD_BUCKET):
  ssm = boto3.client('ssm', region_name=AWS_REGION)
  return ssm.get_parameter(
      Name=bucketPrefix + parameterName,
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
