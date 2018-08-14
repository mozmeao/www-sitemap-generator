FROM python:3.6-slim-stretch

# Extra python env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
CMD ["./generate_sitemap.py"]

COPY ./requirements.txt ./
RUN pip install --require-hashes --no-cache-dir -r requirements.txt
