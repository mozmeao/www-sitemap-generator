FROM python:3.6-slim-stretch

# Extra python env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV AIOHTTP_NO_EXTENSIONS=1

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --require-hashes --no-cache-dir -r requirements.txt
