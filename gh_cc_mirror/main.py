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


class MirrorRepo:
    def __init__(self, name, desc, last_updated, https_url, repo_dir):
        self.name = name
        self.last_updated = last_updated
        self.desc = desc
        self.https_url = https_url
        self.dir = repo_dir

class Gitlab(object):

    def __init__(self, token, groups, host, within=None):
        self.token = token
        self.groups = groups.split(",")
        self.host = host
        self.within = within

    def _get_diff_last_update(self, date_str):
        diff = (datetime.utcnow()-datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ"))
        return diff.total_seconds()/60

    def _filter(self, repos):
        result = []
        for repo in repos:
            # filter within time range
            if self.within and self._get_diff_last_update(repo["last_activity_at"]) > self.within:
                continue

            # make repo object
            name = "gitlab-{}".format(repo["name"])
            https_url = repo["http_url_to_repo"].replace("https://", "https://gitlab-ci-token:{}@".format(self.token))
            repo_dir = "{}.git".format(repo["name"])

            result.append(
                MirrorRepo(name, repo["description"], repo["last_activity_at"], https_url, repo_dir)
            )

        return result

    def get_repos(self):
        repos = []
        headers = {
            "private-token": self.token,
        }
        for group_id in self.groups:
            response = requests.get(
                '{}/api/v4/groups/{}/projects?simple=true'.format(self.host, group_id),
                headers=headers)
            response.raise_for_status()
            repos = repos + response.json()

        return self._filter(repos)


class CodeCommit(object):

    def __init__(self, client, user, password):
        self.client = client
        self.user = user
        self.password = password
        self.repos = []

    def get_repos(self):
        if self.repos:
            return self.repos

        self.repos = []
        for repo in self.client.list_repositories().get("repositories", []):
            self.repos.append(repo["repositoryName"])
        return self.repos

    def mirror(self, repo):
        self._prepare_repo(repo.name, repo.desc)
        self._handle_local_clone(repo.dir, repo.name, repo.https_url)
        self._push_to_mirror(repo.dir, repo.name)

    def _prepare_repo(self, name, desc=None):
        if name not in self.get_repos():
            logger.info("\t* Create AWS repo: {}".format(name))
            resp = self.client.create_repository(
                    repositoryName=name,
                    repositoryDescription=desc or "")
            return True
        return False

    def _handle_local_clone(self, repo_dir, name, https_url):
        if not os.path.exists(repo_dir):
            logger.info("\t* Creating local bare clone for {}".format(name))
            os.mkdir(repo_dir)
            Git().clone("--bare", https_url)
        else:
            logger.info("\t* Fetching updates for repository {}".format(name))
            logger.info(https_url)
            logger.info(repo_dir)
            g = Repo(repo_dir).git
            g.fetch("origin",  "+refs/heads/*:refs/heads/*", "--prune")

    def _push_to_mirror(self, repo_dir, name):
        logger.info("\t* Mirror local bare clone {}".format(name))
        g = Repo(repo_dir).git
        resp = g.push("--mirror",  "https://{user}:{pwd}@git-codecommit.eu-central-1.amazonaws.com/v1/repos/{name}".format(
                    user=self.user, pwd=self.password, name=name
        ))


class GitSync(object):

    def __init__(self, aws_client, args):
        self.cc = CodeCommit(aws_client, args.cc_user, args.cc_password)

        within = int(args.pushed_within) if args.pushed_within else None
        if args.gitlab_token:
            self.source = Gitlab(args.gitlab_token, args.gitlab_groups, args.gitlab_host, within)
        else:
            assert 1 == 0
            #self.source = Gitlab(args.gitlab_token, args.gitlab_groups, args.gitlab_host, within)

    def run_sync(self):
        gl_repos = self.source.get_repos()
        for repo in gl_repos:
            logger.info("Handling {}, last pushed at {}".format(repo.name, repo.last_updated))
            self.cc.mirror(repo)

def main():
    # read cli arguments
    arg_desc = """\n
    This command will mirror all repositories of an organization from Github to AWS CodeCommit. 
    This script is intended to run as a cronjob, typically.
    """
    parser = argparse.ArgumentParser(arg_desc)
    required = parser.add_argument_group('required named arguments')
    required.add_argument("--cc-user", help="CodeCommit user name", required=True)
    required.add_argument("--cc-password", help="CodeCommit password", required=True)
    required.add_argument("--gitlab-token", help="Gitlab personal API access token", required=True)
    required.add_argument("--gitlab-groups", help="Gitlab groups, comma-separated string of groupd ids.", required=True)
    parser.add_argument("--gitlab-host", help="Gitlab host, default https://gitlab.com", default="https://gitlab.com")
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


    GitSync(aws_client, args).run_sync()

if __name__ == "__main__":
    main()
