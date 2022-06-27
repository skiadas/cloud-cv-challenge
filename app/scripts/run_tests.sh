#!/bin/sh
QUEUE_NAME=test-resume-incoming-request-queue \
 sam local invoke "IncomingRequestFunction" -e app/tests/event1.json --template cloudFormation/counters.yaml
