#!/bin/bash

set -exo pipefail

if [[ "$1" == "commit" ]]; then
    # get latest from github
    git fetch https://github.com/mozmeao/www-sitemap-generator.git master
    git checkout -f FETCH_HEAD
fi

docker build --pull \
             -t sitemap-generator \
             --build-arg "USER_ID=$(id -u):$(id -g)" \
             .

docker run --rm \
           --env-file .bedrock.env \
           -v "$PWD/data:/app/sitemap-data" \
           sitemap-generator ./run-generator.sh

if [[ "$1" == "commit" ]]; then
    if git status --porcelain | grep -E "\.json\$"; then
        git add data
        git commit -m "Update sitemaps data"
        git push git@github.com:mozmeao/www-sitemap-generator.git HEAD:master
        echo "Sitemap data update committed"
    else
        echo "No new sitemap data"
    fi
fi

if [[ -n "$SNITCH_URL" ]]; then
    curl "$SNITCH_URL"
fi
