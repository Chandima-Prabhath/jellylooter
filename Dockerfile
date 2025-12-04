FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY looter_app.py .
COPY templates/ templates/
COPY static/ static/

RUN mkdir -p /config /storage

EXPOSE 5000

ENV PYTHONUNBUFFERED=1

CMD ["python", "looter_app.py"]
