#!/bin/bash
set -ex
bin/run-db-download.py
python manage.py l10n_update
python manage.py update_sitemaps
python update_sitemap_json.py
