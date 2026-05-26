FROM python:3.13-slim

WORKDIR /futdatamanager

RUN apt-get update && apt-get install -y postgresql-client gettext && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY create_superuser.sh /futdatamanager/
RUN chmod +x /futdatamanager/create_superuser.sh

COPY . .

RUN python manage.py compilemessages

EXPOSE 8000

ENTRYPOINT ["/futdatamanager/start_app.sh"]
