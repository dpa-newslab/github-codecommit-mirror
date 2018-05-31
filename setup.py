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
from setuptools import setup, find_packages

version = "0.2.0"
setup(name='github-codecommit-mirror',
    version=version,
    description='Mirror all repositories of a Github organization or Gitlab groups to AWS CodeCommit, including branches.',
    classifiers=[
            "Programming Language :: Python :: 3.5",
            'Development Status :: 4 - Beta',
            'Intended Audience :: System Administrators',
            'Topic :: Terminals',
                "Operating System :: POSIX :: Linux",
                "Environment :: Console",
            ],
    keywords=['git','github','gitlab','codecommit', 'mirror', 'sync'],
    author='dpa-infocom GmbH',
    maintainer='Martin Borho',
    maintainer_email='martin@borho.net',
    url='https://github.com/dpa-newslab/github-codecommit-mirror',
    license='Apache Software License (http://www.apache.org/licenses/LICENSE-2.0)',
    packages=find_packages(exclude=['tests', 'htmlcov', 'dist',]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "GitPython==2.1.5",
        "boto3==1.4.6",
        "requests==2.18.4",
    ],
    entry_points="""
            [console_scripts]
            gh-cc-mirror = gh_cc_mirror:cmd_github
            gl-cc-mirror = gh_cc_mirror:cmd_gitlab
    """,
)
