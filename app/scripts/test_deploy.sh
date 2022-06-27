#!/bin/sh
# Starts a stack deployment
# MUST BE RUN FROM MAIN PROJECT LOCATION
# MUST HAVE SET AWS_PROFILE VARIABLE OR OTHERWISE
# MAKE SURE CURRENT PROFILE HAS ACCESS
sam sync --template ./cloudFormation/counters.yaml --stack-name test-stack --watch \
  --beta-features
