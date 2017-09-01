# -*- coding: utf-8 -*-
#
# Copyright 2017 dpa-infocom GmbH
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
import requests
import time
import logging
from requests.auth import HTTPBasicAuth
from datetime import datetime
from git import Repo, Git

# setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger.addHandler(ch)
logging.getLogger('botocore').setLevel(logging.ERROR)
logging.getLogger('git').setLevel(logging.INFO)

# read cli arguments
arg_desc = """\n
This command will mirror all repositories of an organization from Github to AWS CodeCommit. 
This script is intended to run as a cronjob, typically.
"""
parser = argparse.ArgumentParser(arg_desc)
required = parser.add_argument_group('required named arguments')
required.add_argument("--cc-user", help="CodeCommit user name", required=True)
required.add_argument("--cc-password", help="CodeCommit password", required=True)
required.add_argument("--github-user", help="Github user account", required=True)
required.add_argument("--github-token", help="Github personal API access token", required=True)
required.add_argument("--github-organization", help="Github organization", required=True)
parser.add_argument("--dir", help="Working directory")
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

def main():
    GitSync().run_sync()

class GitSync(object):

    aws_client = aws_client
    cc_user = args.cc_user
    cc_password = args.cc_password
    gh_user = args.github_user
    gh_token = args.github_token
    gh_org = args.github_organization
    within = int(args.pushed_within) if args.pushed_within else None

    def _get_diff_last_update(self, date_str):
        diff = (datetime.utcnow()-datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ"))
        return diff.total_seconds()/60

    def _get_gh_query(self):
        return """query {organization(login:"%s") {repositories(
                    last:100, isFork: false,
                    orderBy: { field: PUSHED_AT, direction: DESC }
                ) {edges {node { name, description, pushedAt}}}}}""" % (self.gh_org)

    def _get_gh_repos(self):
        query = {"query": self._get_gh_query()}
        response = requests.post('https://api.github.com/graphql', json=query,
                                auth=HTTPBasicAuth(self.gh_user, self.gh_token))
        response.raise_for_status()
        return response.json()

    def _get_aws_repos(self):
        aws_repos = []
        for repo in self.aws_client.list_repositories().get("repositories", []):
            aws_repos.append(repo["repositoryName"])
        return aws_repos

    def run_sync(self):
        gh_repos = self._get_gh_repos()
        for repo in gh_repos.get("data",{}).get("organization",{}).get("repositories",{}).get("edges", {}):
            if self.within and self._get_diff_last_update(repo["node"]["pushedAt"]) > self.within:
                # if within specified, do filtering
                continue
            logger.info("Handling {}, last pushed at {}".format(repo["node"]["name"], repo["node"]["pushedAt"]))
            repository = Repository(repo["node"]["name"], repo["node"]["description"], repo["node"]["pushedAt"])
            repository.sync()


class Repository(GitSync):

    def __init__(self, name, desc, pushed_at):
        self.name = name
        self.desc = desc
        self.pushed_at = pushed_at
        self.repo_dir = "{}.git".format(self.name)
        self.aws_repos = self._get_aws_repos()

    def sync(self):
        self._handle_local_clone()
        self._handle_aws_repo()
        self._push_to_mirror()

    def _handle_local_clone(self):
        if not os.path.exists(self.repo_dir):
            logger.info("\t* Creating local bare clone for {}".format(self.name))
            Git().clone("--bare", "https://{user}:{pwd}@github.com/{org}/{name}.git".format(
                                    user=self.gh_user,
                                    pwd=self.gh_token,
                                    org=self.gh_org,
                                    name=self.name))
        else:
            logger.info("\t* Fetching updates for repository {}".format(self.name))
            g = Repo(self.repo_dir).git
            g.fetch("origin",  "+refs/heads/*:refs/heads/*", "--prune")

    def _handle_aws_repo(self):
        if self.name not in self.aws_repos:
            logger.info("\t* Create AWS repo: {}".format(self.name))
            resp = self.aws_client.create_repository(
                    repositoryName=self.name,
                    repositoryDescription=self.desc or "")
            return True
        return False

    def _push_to_mirror(self):
        logger.info("\t* Mirror local bare clone {}".format(self.name))
        g = Repo(self.repo_dir).git
        g.push("--mirror",  "https://{user}:{pwd}@git-codecommit.eu-central-1.amazonaws.com/v1/repos/{name}".format(
                    user=self.cc_user, pwd=self.cc_password, name=self.name
        ))


if __name__ == "__main__":
    main()
