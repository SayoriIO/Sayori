FROM python:3.11.1

RUN apt update &&  apt install curl && \
    pip install -r requirements.txt & \
    curl -L https://fly.io/install.sh | sh;
