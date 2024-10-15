FROM mozmeao/bedrock:prod-latest
USER root
COPY settings_local.py bedrock/settings/local.py
COPY update_sitemap_json.py sitemap_utils.py bin/run-generator.sh ./
ARG USER_ID=1000:1000
ENV USER_ID=${USER_ID}
RUN chown -R "${USER_ID}" /app
USER ${USER_ID}
