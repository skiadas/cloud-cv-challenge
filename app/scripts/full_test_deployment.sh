#!/bin/sh
# MUST BE RUN FROM MAIN PROJECT LOCATION
# MUST HAVE SET AWS_PROFILE VARIABLE OR OTHERWISE
# MAKE SURE CURRENT PROFILE HAS ACCESS

aws cloudformation package \
  --template-file ./cloudFormation/main.yaml \
  --s3-bucket skiadas-resume-templates \
  --output-template-file packaged-dev.template || exit 0
aws cloudformation deploy \
  --stack-name skiadas-resume-dev-stack \
  --s3-bucket skiadas-resume-templates \
  --template-file packaged-dev.template \
  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
  --parameter-overrides BucketName=skiadas-resume-dev-bucket EnvType=test

