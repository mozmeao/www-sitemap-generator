#!/bin/bash
set -exo pipefail
urlwait http://bedrock:8000/ 60
python update_etags.py
python generate_sitemaps.py
