FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends jq && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY run.sh .
RUN chmod +x run.sh

EXPOSE 8502

CMD ["sh", "run.sh"]
