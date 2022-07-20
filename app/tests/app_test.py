import json
# from client import get_client
from moto import mock_sqs, mock_dynamodb
from app import process_incoming_request, process_sqs_message, read_db_data, encode_query_string
from sqs_queue import sqs_queue
from dynamodb import dbtable
import pytest
import os

QUEUE_NAME = 'test-queue'

@mock_sqs
def test_record_to_queue(aws_credentials, request_cf):
  queue = sqs_queue(QUEUE_NAME)
  process_incoming_request(json.loads(request_cf), queue.get_url())
  # Verify SQS called
  assert queue.get_attribute('ApproximateNumberOfMessages') == '1'
  expected_json = { "ip": "203.0.113.178", "path": "/" }
  assert json.loads(queue.get_next_message_body()) == expected_json

@mock_dynamodb
def test_sqs_message_updates_db(aws_credentials, table_names):
  path_table = dbtable.create(table_names['SITE_COUNTS'], 'path')
  ip_table = dbtable.create(table_names['IP_COUNTS'], 'ip')
  total_table = dbtable.create(table_names['TOTAL_COUNT'], 'total')
  process_sqs_message("{ \"ip\": \"203.0.113.178\", \"path\": \"/\" }")
  process_sqs_message("{ \"ip\": \"203.0.113.178\", \"path\": \"/home\" }")
  process_sqs_message("{ \"ip\": \"203.0.113.174\", \"path\": \"/\" }")
  assert path_table.get("/") == 2
  assert path_table.get("/home") == 1
  assert path_table.entries_count() == 2
  assert ip_table.get("203.0.113.178") == 2
  assert ip_table.get("203.0.113.174") == 1
  assert ip_table.entries_count() == 2
  assert total_table.get("total") == 3


@mock_dynamodb
def test_data_retrieval(aws_credentials, table_names):
    path_table = dbtable.create(table_names['SITE_COUNTS'], 'path')
    ip_table = dbtable.create(table_names['IP_COUNTS'], 'ip')
    total_table = dbtable.create(table_names['TOTAL_COUNT'], 'total')
    path_table.setCount('/site', 1)
    ip_table.setCount('203.123.111.3', 2)
    total_table.setCount('total', 3)
    assert read_db_data({'ip': '203.123.111.3', 'path': '/site' }) == { 'total': 3, 'ip': 2, 'path': 1}

def test_query_string_from_obj(query_string):
    expected = "?ID=42&NoValue=&querymv=val1&querymv=val2"
    assert encode_query_string(query_string) == expected

@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture(scope='function')
def table_names():
    """Provided table names for function to use."""
    values = {
      'SITE_COUNTS': 'test-site-counts',
      'TOTAL_COUNT': 'test-total-count',
      'IP_COUNTS': 'test-ip-counts'
    }
    os.environ.update(values)
    return values

@pytest.fixture(scope="function")
def request_cf():
  return '''
    {
      "clientIp": "203.0.113.178",
      "headers": {
        "host": [
          {
            "key": "Host",
            "value": "d111111abcdef8.cloudfront.net"
          }
        ],
        "user-agent": [
          {
            "key": "User-Agent",
            "value": "curl/7.66.0"
          }
        ],
        "accept": [
          {
            "key": "accept",
            "value": "*/*"
          }
        ]
      },
      "method": "GET",
      "querystring": "",
      "uri": "/"
    }
    '''

@pytest.fixture(scope="function")
def query_string():
  return {
      "ID": { "value": "42" },
      "NoValue": { "value": "" },
      "querymv": {
        "value": "val1",
        "multiValue": [
          {
            "value": "val1"
          },
          {
            "value": "val2"
          }
        ]
      }
  }

# This all belongs somewhere else
# As part of some integration tests
  # response = get_client(True).invoke(
  #   FunctionName="IncomingRequestFunction",
  #   Payload=data
  #   )

  # Verify the response
  # assert response['StatusCode'] == 200
  # assert json.loads(response['Payload'].read()) == json.loads(data)['Records'][0]['cf']['request']
