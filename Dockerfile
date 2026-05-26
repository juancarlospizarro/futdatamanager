FROM python:3.13-slim

WORKDIR /football_stats_app

RUN apt-get update && apt-get install -y postgresql-client gettext && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY create_superuser.sh /football_stats_app/
RUN chmod +x /football_stats_app/create_superuser.sh

COPY . .

RUN python manage.py compilemessages

RUN sed -i 's/\r$//' /football_stats_app/start_app.sh
RUN chmod +x /football_stats_app/start_app.sh

EXPOSE 8000

ENTRYPOINT ["/football_stats_app/start_app.sh"]
