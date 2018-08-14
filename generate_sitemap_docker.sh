#!/bin/bash

set -exo pipefail

IMAGE_NAME="mozmeao/generate-sitemap:latest"

docker build -t "$IMAGE_NAME" --pull .
docker run --rm -v "$PWD:/app" "$IMAGE_NAME"
