FROM python:latest

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

ADD . /app
RUN python manage.py makemigrations && python manage.py migrate

EXPOSE 8000
CMD gunicorn --bind :8000 totoro.wsgi:application
