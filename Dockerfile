FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY looter_app.py .

# Copy templates (required)
COPY templates/ templates/

# Create directories
RUN mkdir -p /config /storage static

EXPOSE 5000

ENV PYTHONUNBUFFERED=1

CMD ["python", "looter_app.py"]
