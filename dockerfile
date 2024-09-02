FROM python:3.8-slim

WORKDIR /python

COPY . /python

RUN pip install fuzzywuzzy pandas playwright

RUN playwright install --with-deps

ENV CHROMIUM_PATH=/home/runner/.cache/ms-playwright/chromium-1129/chrome-linux