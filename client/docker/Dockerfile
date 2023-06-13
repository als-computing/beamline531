FROM python:3.9
MAINTAINER ALS
COPY docker/requirements.txt requirements.txt

RUN apt update
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

WORKDIR /app/work
ENV PYTHONPATH ./
COPY src src