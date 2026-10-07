#!/bin/bash

set -e

REGION="us-east-1"
INSTANCE_ID="i-030b67f47c9078753"
ECR_REGISTRY="377587329790.dkr.ecr.us-east-1.amazonaws.com"
ECR_REPOSITORY="cloud-task-app"
IMAGE_TAG="$1"

if [ -z "$IMAGE_TAG" ]; then
  echo "ERROR: Image tag is required."
  exit 1
fi

COMMAND_ID=$(aws ssm send-command \
  --region "$REGION" \
  --instance-ids "$INSTANCE_ID" \
  --document-name "AWS-RunShellScript" \
  --parameters "commands=[
    \"cd /opt/cloud-task-app\",
    \"sed -i 's/^IMAGE_TAG=.*/IMAGE_TAG=$IMAGE_TAG/' .env\",
    \"aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REGISTRY\",
    \"docker compose -f docker-compose.prod.yml pull web\",
    \"docker compose -f docker-compose.prod.yml up -d web\",
    \"docker image prune -f\"
  ]" \
  --query 'Command.CommandId' \
  --output text)

echo "SSM Command ID: $COMMAND_ID"

aws ssm wait command-executed \
  --region "$REGION" \
  --command-id "$COMMAND_ID" \
  --instance-id "$INSTANCE_ID"

aws ssm get-command-invocation \
  --region "$REGION" \
  --command-id "$COMMAND_ID" \
  --instance-id "$INSTANCE_ID"
