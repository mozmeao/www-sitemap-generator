#!/bin/bash
set -exo pipefail
urlwait http://bedrock:8000/ 120
sleep 5
python update_etags.py
python generate_sitemaps.py
