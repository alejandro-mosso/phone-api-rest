FROM amancevice/pandas:1.0.0
#FROM python:3.7-alpine

MAINTAINER Alejandro Mosso.

ENV PYTHONUNBUFFERED 1

# Install dependencies
USER root
# RUN apt-get install gcc g++ libc-dev linux-headers python3-dev \
#    libwebp-dev libjpeg zlib


COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Setup directory structure
RUN mkdir /app
WORKDIR /app
COPY ./app/ /app

