#!/bin/sh

sam local invoke "IncomingRequestFunction" -e app/tests/event_cf.json \
  --template cloudFormation/counters.yaml \
  --env-vars app/tests/test_env.json
