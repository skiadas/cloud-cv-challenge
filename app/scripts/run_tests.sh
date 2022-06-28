#!/bin/sh

sam local invoke "IncomingRequestFunction" -e app/tests/event1.json \
  --template cloudFormation/counters.yaml \
  --env-vars app/tests/test_env.json
