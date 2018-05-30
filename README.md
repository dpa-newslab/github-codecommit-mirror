# Github - Gitlab - AWS CodeCommit - Mirror

CLI-Commands for mirroring all repositories of a **Github** organization or a **Gitlab** group to **AWS CodeCommit**. 

These commands are intended to run as a cronjob, typically.

## Installation
Python >= 3.5 is required. 

```sh
pip install gh-cc-mirror
```

Two commands are available after installing:

* **gh-cc-mirror** (Github -> CodeCommit)
* **gl-cc-mirror** (Gitlab -> CodeCommit)

## Usage Github => CodeCommit

```sh
$ gh-cc-mirror -h
usage: 

    This command will mirror all repositories of an organization from Github to AWS CodeCommit.
    This script is intended to run as a cronjob, typically.
    
       [-h] --github-user GITHUB_USER --github-token GITHUB_TOKEN
       --github-organization GITHUB_ORGANIZATION --cc-user CC_USER
       --cc-password CC_PASSWORD [--dir DIR] [--prefix PREFIX]
       [--aws-access-key AWS_ACCESS_KEY]
       [--aws-secret-access-key AWS_SECRET_ACCESS_KEY]
       [--aws-region AWS_REGION] [--pushed-within PUSHED_WITHIN]

optional arguments:
  -h, --help            show this help message and exit
  --dir DIR             Working directory
  --prefix PREFIX       Prefix for CodeCommit repository name.
  --aws-access-key AWS_ACCESS_KEY
                        AWS access key
  --aws-secret-access-key AWS_SECRET_ACCESS_KEY
                        AWS secret access key
  --aws-region AWS_REGION
                        AWS region
  --pushed-within PUSHED_WITHIN
                        Limit repositories with changes pushed with given
                        period, in minutes!

required named arguments:
  --github-user GITHUB_USER
                        Github user account
  --github-token GITHUB_TOKEN
                        Github personal API access token
  --github-organization GITHUB_ORGANIZATION
                        Github organization
  --cc-user CC_USER     CodeCommit user name
  --cc-password CC_PASSWORD
                        CodeCommit password
```

## Usage Gitlab => CodeCommit

```sh
$ gl-cc-mirror -h
usage: 

    This command will mirror all repositories of groups from Gitlab to AWS CodeCommit.
    This script is intended to run as a cronjob, typically.
    
       [-h] --gitlab-token GITLAB_TOKEN --gitlab-groups GITLAB_GROUPS
       [--gitlab-host GITLAB_HOST] --cc-user CC_USER --cc-password CC_PASSWORD
       [--dir DIR] [--prefix PREFIX] [--aws-access-key AWS_ACCESS_KEY]
       [--aws-secret-access-key AWS_SECRET_ACCESS_KEY]
       [--aws-region AWS_REGION] [--pushed-within PUSHED_WITHIN]

optional arguments:
  -h, --help            show this help message and exit
  --gitlab-host GITLAB_HOST
                        Gitlab host, default https://gitlab.com
  --dir DIR             Working directory
  --prefix PREFIX       Prefix for CodeCommit repository name.
  --aws-access-key AWS_ACCESS_KEY
                        AWS access key
  --aws-secret-access-key AWS_SECRET_ACCESS_KEY
                        AWS secret access key
  --aws-region AWS_REGION
                        AWS region
  --pushed-within PUSHED_WITHIN
                        Limit repositories with changes pushed with given
                        period, in minutes!

required named arguments:
  --gitlab-token GITLAB_TOKEN
                        Gitlab personal API access token
  --gitlab-groups GITLAB_GROUPS
                        Gitlab groups, comma-separated string of groupd ids.
  --cc-user CC_USER     CodeCommit user name
  --cc-password CC_PASSWORD
                        CodeCommit password
```

## Authentication

Git connections to **Github**, **Gitlab** and **AWS CodeCommit** are made via **https://**. 

For authentication at **Github**, a [Personal Access Token](https://github.com/settings/tokens) is needed. 

For authentication at **Gitlab**, a [Personal Access Token](https://gitlab.com/profile/personal_access_tokens) with **api** and **read_repository** permissions is needed. 

[HTTPS credentials for CodeCommit](https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-gc.html) have to be generated via [AWS IAM](https://console.aws.amazon.com/iam/home).

## IAM rules

Access rights needed by AWS, for listing and creating CodeCommit repositoires:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "codecommit:CreateRepository",
                "codecommit:List*"
            ],
            "Resource": "*"
        }
    ]
}


```
## License
Copyright 2017, 2018 dpa-infocom GmbH

Apache License, Version 2.0 - see LICENSE for details
