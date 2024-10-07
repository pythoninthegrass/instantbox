# syntax=docker/dockerfile:1.7.0

FROM python:3.11.10-alpine3.20 AS builder

WORKDIR /app

COPY requirement.txt .

RUN python -m pip install -q --no-cache-dir -r requirement.txt -t ./

COPY . .

COPY manifest.json .

FROM python:3.11.10-alpine3.20

ENV SERVERURL ""

WORKDIR /app

COPY --from=builder /app/ .

EXPOSE 65501

CMD ["inspire.py"]

ARG BUILD_DATE
ARG VCS_REF

LABEL org.opencontainers.image.title="instantbox"
LABEL org.label-schema.name="instantbox"
LABEL maintainer="pythoninthegrass <4097471+pythoninthegrass@users.noreply.github.com>"
LABEL org.label-schema.build-date=$BUILD_DATE
LABEL org.label-schema.vcs-ref=$VCS_REF
