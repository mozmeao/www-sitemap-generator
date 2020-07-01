FROM mozmeao/bedrock:prod-latest
USER root
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY templates ./templates
COPY settings_local.py bedrock/settings/local.py
COPY generate_sitemaps.py update_etags.py sitemap_utils.py bin/run-generator.sh ./
