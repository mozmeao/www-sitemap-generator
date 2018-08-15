#!/bin/bash

set -x

docker-compose pull bedrock
docker-compose build --pull generator
docker-compose run --rm -u "$(id -u)" generator

# store return code from this command so we can use it after we clean up
RETCODE="$?"

docker-compose kill
docker-compose rm -sf

exit $RETCODE
