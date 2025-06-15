# backend/Dockerfile
FROM python:3.11-slim

# żeby mieć pg_isready
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client gcc libpq-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# entrypoint.sh ma już 'chmod +x' założony
ENTRYPOINT ["./entrypoint.sh"]
