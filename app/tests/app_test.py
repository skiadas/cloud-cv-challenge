import json
# from client import get_client
from moto import mock_sqs
from app import process_incoming_request
from sqs_queue import sqs_queue
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


@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

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

# This all belongs somewhere else
# As part of some integration tests
  # response = get_client(True).invoke(
  #   FunctionName="IncomingRequestFunction",
  #   Payload=data
  #   )

  # Verify the response
  # assert response['StatusCode'] == 200
  # assert json.loads(response['Payload'].read()) == json.loads(data)['Records'][0]['cf']['request']
