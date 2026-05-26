FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client gettext && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY create_superuser.sh /app/
RUN chmod +x /app/create_superuser.sh

COPY . .

RUN python manage.py compilemessages

RUN sed -i 's/\r$//' /app/start_app.sh
RUN chmod +x /app/start_app.sh

EXPOSE 8000

ENTRYPOINT ["/app/start_app.sh"]
