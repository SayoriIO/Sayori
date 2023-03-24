FROM python:latest

RUN apt update &&  apt -y install curl redis

USER root

RUN curl -L https://fly.io/install.sh | sh;

ENV PATH="/root/.fly:$PATH"
