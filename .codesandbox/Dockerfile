FROM python:latest

RUN pip install pipenv

USER root

RUN curl -L https://fly.io/install.sh | sh;

ENV PATH="/root/.fly:$PATH"
