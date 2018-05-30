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
from requests.auth import HTTPBasicAuth
from datetime import datetime
from .repo import MirrorRepo

class Github(object):

    def __init__(self, token, org, user, within=None):
        self.token = token
        self.org = org
        self.user = user
        self.within = within

    def _get_diff_last_update(self, date_str):
        diff = (datetime.utcnow()-datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ"))
        return diff.total_seconds()/60

    def _filter(self, repos):
        result = []
        for repo in repos:
            # filter within time range
            last_updated = repo["node"]["pushedAt"]
            if self.within and self._get_diff_last_update(last_updated) > self.within:
                continue

            # make repo object
            name = repo["node"]["name"]
            https_url = "https://{user}:{pwd}@github.com/{org}/{name}.git".format(
                                    user=self.user,
                                    pwd=self.token,
                                    org=self.org,
                                    name=name)
            repo_dir = "{}.git".format(name)

            result.append(
                MirrorRepo(name, repo["node"]["description"], last_updated, https_url, repo_dir)
            )
        return result

    def _get_query(self):
        return """query {organization(login:"%s") {repositories(
                    last:100, isFork: false,
                    orderBy: { field: PUSHED_AT, direction: DESC }
                ) {edges {node { name, description, pushedAt}}}}}""" % (self.org)

    def get_repos(self):
        query = {"query": self._get_query()}
        response = requests.post('https://api.github.com/graphql', json=query,
                                auth=HTTPBasicAuth(self.user, self.token))
        response.raise_for_status()
        api_res = response.json()

        repos = api_res.get("data",{}).get("organization",{}).get("repositories",{}).get("edges", {})
        return self._filter(repos)

