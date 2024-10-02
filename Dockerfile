FROM python:3.12-alpine

ARG VERSION

RUN pip --no-cache-dir --retries=5 install neojelll-url-shortener-api==$VERSION

ENTRYPOINT ["neojelll-url-shortener-api"]
