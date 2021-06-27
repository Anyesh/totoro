FROM python:3.9

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

ADD . /app
RUN mv wait-for /bin/wait-for

EXPOSE 8000
