FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client gcc libpq-dev netcat-openbsd \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["./entrypoint.sh"]
