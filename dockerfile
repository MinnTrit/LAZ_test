FROM python:3.8-slim

WORKDIR /python

COPY . /python

RUN pip install fuzzywuzzy \
pip install pandas \
pip install playwright

ENV CHROMIUM_PATH=/home/runner/.cache/ms-playwright/chromium-1129/chrome-linux