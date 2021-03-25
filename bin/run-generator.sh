#!/bin/bash
set -ex
bin/run-db-download.py
python manage.py l10n_update
python manage.py update_sitemaps
sed -i -E -e 's|<html class="windows x86 no-js".+>|<html class="windows x86 no-js">|' bedrock/base/templates/base-protocol.html
# needed for app to start
touch data/last-run-update_locales data/last-run-download_database
bin/run-prod.sh > /dev/null &
urlwait http://localhost:8000 60
sleep 2
python update_etags.py
