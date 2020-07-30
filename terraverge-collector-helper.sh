#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage $0 <json plan location>"
    exit 1
fi

if [ ! -r $1 ]; then
    echo "Unable to read plan : $1"
    exit 2
fi

if [ -z "$TERRAVERGE_COLLECTOR_URL" ] || [ -z "$TERRAVERGE_COLLECTOR_PSK" ]; then
    echo "Please specify TERRAVERGE_COLLECTOR_URL and TERRAVERGE_COLLECTOR_PSK"
    exit 3
fi


# Check terraform version
if [ -f .terraform-version ]; then
    # Read .terraform-version
    terraform_version=$(cat .terraform-version)
else
    # try to find terraform version with cli
    terraform_version=$(terraform version | head -n 1 | cut -f 2 -d ' ' | cut -f 2 -d 'v')
fi

# Check if we are in a gitlab pipeline
if [ -n "$CI_SERVER" ]; then
    git_remote=$CI_REPOSITORY_URL
    git_commit=$CI_COMMIT_SHA
    ci_url=$CI_JOB_URL
    event=$CI_PIPELINE_SOURCE
    pipeline=$CI_PIPELINE_URL
    branch=$CI_COMMIT_REF_NAME
    source="terraverge-collector-helper.sh triggered on branch $branch by a '$event' event. Pipeline URL : $pipeline"
else
    # fallback to git cli
    remotes=$(git remote -v | awk '{print $2}' | sort | uniq)
    git_remote=$(echo -n "$(echo $remotes)" | tr '\n' ',')
    git_commit=$(git rev-parse HEAD)
    ci_url=""
    event=""
    pipeline=""
    branch=$(git rev-parse --abbrev-ref HEAD)
    source="terraverge-collector-helper.sh triggered by hand outside gitlab from $(pwd)"

fi

# Fetch date of plan
generation_date=$(date -d "@$(stat -c %Y $1)" --iso-8601=seconds)

# Get workspace
workspace="$git_remote/$(git rev-parse --show-prefix)"

# Post plan
curl -X POST \
    --form-string "psk=$TERRAVERGE_COLLECTOR_PSK" \
    --form-string "terraform_version=$terraform_version" \
    --form-string "git_remote=$git_remote" \
    --form-string "git_commit=$git_commit" \
    --form-string "ci_url=$ci_url" \
    --form-string "source=$source" \
    --form-string "generation_date=$generation_date" \
    --form-string "workspace=$workspace" \
    -F plan=@$1 \
    $TERRAVERGE_COLLECTOR_URL
