
FROM python:3.9.12-slim

WORKDIR /code

COPY . /code

RUN python3 -m pip install -r requirements.txt

