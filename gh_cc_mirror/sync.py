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
from .codecommit import CodeCommit
from .github import Github
from .gitlab import Gitlab

logger = logging.getLogger(__name__)

class GitSync(object):

    def __init__(self, aws_client, args):
        self.cc = CodeCommit(aws_client, args.cc_user, args.cc_password, args.prefix)
        self.source = None

        within = int(args.pushed_within) if args.pushed_within else None
        if hasattr(args, "gitlab_token"):
            self.source = Gitlab(
                args.gitlab_token, args.gitlab_groups, args.gitlab_host, within
            )
        elif hasattr(args, "github_token"):
            self.source = Github(
                args.github_token, args.github_organization, args.github_user, within
            )
        assert self.source is not None

    def run_sync(self):
        gl_repos = self.source.get_repos()
        for repo in gl_repos:
            try:
                logger.info("Handling {}, last pushed at {}".format(repo.name, repo.last_updated))
                self.cc.mirror(repo)
            except Exception as exc:
                logger.error("Error when handling {}, got {}".format(repo.name, exc))


