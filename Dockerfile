FROM python:3.11-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR src/app/

COPY src/requirements.txt .

RUN pip3 install --upgrade pip && pip install -r requirements.txt

COPY src/ .