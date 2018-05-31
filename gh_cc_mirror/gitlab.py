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
import requests
from datetime import datetime
from .repo import MirrorRepo

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
            https_url = repo["http_url_to_repo"].replace("https://", "https://gitlab-ci-token:{}@".format(self.token))
            repo_dir = "{}.git".format(repo["name"])
            desc = "{}\n{}".format(repo["path_with_namespace"], repo["description"] or "")

            result.append(
                MirrorRepo(repo["name"], desc, repo["last_activity_at"], https_url, repo_dir)
            )

        return result

    def get_repos(self):
        repos = []
        headers = {
            "private-token": self.token,
        }
        for group_id in self.groups:
            call_url = "{}/api/v4/groups/{}/projects?simple=true&order_by=last_activity_at".format(
                            self.host, group_id)
            response = requests.get(call_url, headers=headers, timeout=60)
            response.raise_for_status()
            repos = repos + response.json()

        return self._filter(repos)
