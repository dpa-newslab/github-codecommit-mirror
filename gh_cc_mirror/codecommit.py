# -*- coding: utf-8 -*-
#
# Copyright 2018 dpa-infocom GmbH
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
import logging
import os
from git import Repo, Git

logger = logging.getLogger(__name__)

class CodeCommit(object):

    def __init__(self, client, user, password, prefix):
        self.client = client
        self.user = user
        self.password = password
        self.repos = []
        self.prefix = prefix

    def get_repos(self):
        if self.repos:
            return self.repos

        self.repos = []
        for repo in self.client.list_repositories().get("repositories", []):
            self.repos.append(repo["repositoryName"])
        return self.repos

    def mirror(self, repo):
        name = "{}{}".format(self.prefix, repo.name) if self.prefix else repo.name
        self._prepare_repo(name, repo.desc)
        self._handle_local_clone(repo.dir, name, repo.https_url)
        self._push_to_mirror(repo.dir, name)

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
            g = Repo(repo_dir).git
            g.fetch("origin",  "+refs/heads/*:refs/heads/*", "--prune")

    def _push_to_mirror(self, repo_dir, name):
        logger.info("\t* Mirror local bare clone {}".format(name))
        g = Repo(repo_dir).git
        resp = g.push("--mirror",  "https://{user}:{pwd}@git-codecommit.eu-central-1.amazonaws.com/v1/repos/{name}".format(
                    user=self.user, pwd=self.password, name=name
        ))

