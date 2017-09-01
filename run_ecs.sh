#!/bin/bash

# Check that the environment variable has been set correctly
if [ -z "$CONFIG_ENV_FILE" ]; then
  echo >&2 'error: missing CONFIG_ENV_FILE environment variable'
  exit 1
fi

echo "Loading env file from s3 ..."
eval $(aws --region=eu-central-1 s3 cp $CONFIG_ENV_FILE - | sed 's/^/export /')
echo "Running ..."
gh-cc-mirror --github-user=$GH_USER --github-token=$GH_TOKEN --github-organization=$GH_ORG --pushed-within=$PUSHED_WITHIN --cc-user=$CC_USER --cc-password=$CC_PASSWORD --dir=$SYNC_DIR

