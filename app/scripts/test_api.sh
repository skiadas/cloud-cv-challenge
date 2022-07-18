#!/bin/sh
sam sync --template ./cloudFormation/testApi.yaml \
  --stack-name test-api-stack --watch \
  --beta-features \
  --profile admin
