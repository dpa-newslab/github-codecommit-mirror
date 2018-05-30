# -*- coding: utf-8 -*-
#
# Copyright 2017, 2018 dpa-infocom GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
import boto3
import os
import sys
import logging

from .sync import GitSync

# setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger.addHandler(ch)
logging.getLogger('botocore').setLevel(logging.ERROR)
logging.getLogger('git').setLevel(logging.INFO)


def cmd_gitlab():
    arg_desc = """\n
    This command will mirror all repositories of groups from Gitlab to AWS CodeCommit.
    This script is intended to run as a cronjob, typically.
    """
    parser = argparse.ArgumentParser(arg_desc)
    required = parser.add_argument_group('required named arguments')
    required.add_argument("--gitlab-token", help="Gitlab personal API access token", required=True)
    required.add_argument("--gitlab-groups", help="Gitlab groups, comma-separated string of groupd ids.", required=True)
    parser.add_argument("--gitlab-host", help="Gitlab host, default https://gitlab.com", default="https://gitlab.com")
    cmd_run(parser, required)

def cmd_github():
    arg_desc = """\n
    This command will mirror all repositories of an organization from Github to AWS CodeCommit.
    This script is intended to run as a cronjob, typically.
    """
    parser = argparse.ArgumentParser(arg_desc)
    required = parser.add_argument_group('required named arguments')
    required.add_argument("--github-user", help="Github user account", required=True)
    required.add_argument("--github-token", help="Github personal API access token", required=True)
    required.add_argument("--github-organization", help="Github organization", required=True)
    cmd_run(parser, required)

def cmd_run(parser, required):
    required.add_argument("--cc-user", help="CodeCommit user name", required=True)
    required.add_argument("--cc-password", help="CodeCommit password", required=True)
    parser.add_argument("--dir", help="Working directory")
    parser.add_argument("--prefix", help="Prefix for CodeCommit repository name.")
    parser.add_argument("--aws-access-key", help="AWS access key")
    parser.add_argument("--aws-secret-access-key", help="AWS secret access key")
    parser.add_argument("--aws-region", help="AWS region", default="eu-central-1")
    parser.add_argument("--pushed-within", help="Limit repositories with changes pushed with given period, in minutes!")
    args = parser.parse_args()

    # change in directory
    if args.dir:
        os.chdir(args.dir)

    # setup AWS CodeCommit client
    aws_client = boto3.client('codecommit',
                              region_name=args.aws_region,
                              aws_access_key_id=args.aws_access_key,
                              aws_secret_access_key=args.aws_secret_access_key)


    GitSync(aws_client, args).run_sync()
