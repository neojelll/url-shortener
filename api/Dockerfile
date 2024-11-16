FROM python:3.12-alpine

RUN apk add --no-cache gcc musl-dev python3-dev zlib-dev

ARG VERSION

RUN pip install neojelll-url-shortener-api==$VERSION

ENTRYPOINT ["neojelll-url-shortener-api"]
