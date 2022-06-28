#!/bin/sh

mkdir -p logs

sam local start-lambda \
  --template cloudFormation/counters.yaml \
  --env-vars app/tests/test_env.json \
  -l logs/local_lambda.txt

