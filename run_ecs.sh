#!/bin/bash

# Check that the environment variable has been set correctly
if [ -z "$CONFIG_ENV_FILE" ]; then
  echo >&2 'error: missing CONFIG_ENV_FILE environment variable'
  exit 1
fi

echo "Loading env file from s3 ..."
eval $(aws --region=eu-central-1 s3 cp $CONFIG_ENV_FILE - | sed 's/^/export /')
echo "Running ..."
gh-cc-mirror --github-user=$GH_USER --github-token=$GH_TOKEN --github-organization=$GH_ORG --pushed-within=$PUSHED_WITHIN --cc-user=$CC_USER --cc-password=$CC_PASSWORD --dir=$GH_SYNC_DIR
gl-cc-mirror --cc-user $CC_USER --cc-password $CC_PASSWORD --gitlab-token $GL_TOKEN --gitlab-groups $GL_GROUPS --dir $GL_SYNC_DIR --prefix $GL_PREFIX --pushed-within=$PUSHED_WITHIN
