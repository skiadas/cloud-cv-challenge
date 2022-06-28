
# Set "running_locally" flag if you are running the integration test locally
def get_client(running_locally):
  import boto3
  import botocore

  if running_locally:
    # Create Lambda SDK client to connect to appropriate Lambda endpoint
    return boto3.client('lambda',
                        region_name="us-east-1",
                        endpoint_url="http://127.0.0.1:3001",
                        use_ssl=False,
                        verify=False,
                        config=botocore.client.Config(
                          signature_version=botocore.UNSIGNED,
                          read_timeout=30,
                          retries={'max_attempts': 0},
                        )
                        )
  else:
    return boto3.client('lambda')
