FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y curl && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"] 