#!/bin/bash

set -exo pipefail

docker-compose pull bedrock
docker-compose build --pull generator
docker-compose run --rm -u "$(id -u):$(id -g)" generator

if [[ "$1" == "commit" ]]; then
    if git status --porcelain | grep -E "\.(json|xml)\$"; then
        git add sitemap.json etags.json sitemaps
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
