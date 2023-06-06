FROM python:3.9
MAINTAINER ALS
COPY requirements.txt requirements.txt

RUN apt update
RUN apt install -y python3-pip
RUN pip install -r requirements.txt

WORKDIR /app/work
ENV PYTHONPATH ./
COPY src src