#!/bin/bash

###################################################
# build an run tests
###################################################

cd $CI_PROJECT_DIR

github_group_repo="ComputationalRadiationPhysics/gitlab-ci-testproject"

pr_id=$(echo "$CI_BUILD_REF_NAME" | cut -d"/" -f1 | cut -d"-" -f2)
target_branch=$(curl -X GET https://api.github.com/repos/${github_group_repo}/pulls/${pr_id} 2>/dev/null| python3 -c 'import json,sys;obj=json.loads(sys.stdin.read());print(obj["base"]["ref"])')
echo "target_branch=${target_branch}"

git remote add mainline https://github.com/${github_group_repo}.git
git fetch mainline

git config --global user.email "CI-BOT"
git config --global user.name "CI-BOT@hzdr.d"

git rebase mainline/${target_branch}

ls -la
