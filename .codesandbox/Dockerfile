FROM python:latest

RUN apt update &&  apt -y install curl

USER root

RUN curl -L https://fly.io/install.sh | sh;

ENV PATH="/root/.fly:$PATH"
