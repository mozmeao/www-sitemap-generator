#!/bin/bash

set -exo pipefail

IMAGE_NAME="mozmeao/generate-sitemap:latest"

docker build -t "$IMAGE_NAME" --pull .
docker run --rm -v "$PWD:/app" "$IMAGE_NAME" python update_etags.py
docker run --rm -v "$PWD:/app" "$IMAGE_NAME" python generate_sitemaps.py
