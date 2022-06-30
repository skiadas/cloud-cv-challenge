import json
# from client import get_client
from moto import mock_sqs
from app import process_incoming_request
from sqs_queue import sqs_queue

QUEUE_NAME = 'test-queue'

request='''
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

expected_message='''
{
  "ip": "203.0.113.178",
  "path": "/"
}
'''

@mock_sqs
def test_record_to_queue():
  queue = sqs_queue(QUEUE_NAME)
  process_incoming_request(json.loads(request), queue.get_url())
  # Verify SQS called
  assert queue.get_attribute('ApproximateNumberOfMessages') == '1'
  assert json.loads(queue.get_next_message_body()) == json.loads(expected_message)

# This all belongs somewhere else
# As part of some integration tests
  # response = get_client(True).invoke(
  #   FunctionName="IncomingRequestFunction",
  #   Payload=data
  #   )

  # Verify the response
  # assert response['StatusCode'] == 200
  # assert json.loads(response['Payload'].read()) == json.loads(data)['Records'][0]['cf']['request']
