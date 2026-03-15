FROM python:3.11-slim

WORKDIR /football_stats_app

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY create_superuser.sh /football_stats_app/
RUN chmod +x /football_stats_app/create_superuser.sh

COPY . .

EXPOSE 8000

CMD ["gunicorn", "football_stats_app.wsgi:application", "--bind", "0.0.0.0:8000"]
