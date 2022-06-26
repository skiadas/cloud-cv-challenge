def lambda_incoming_to_sqs_handler(event, context):
  request = event['Records'][0]['cf']['request']
  return request
