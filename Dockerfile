FROM python:3.8-slim-buster

# Extra python env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --require-hashes --no-cache-dir -r requirements.txt
