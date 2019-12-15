#!/bin/bash

DOMAIN=$1

openssl req -x509 \
  -newkey rsa:4096 \
  -sha256 \
  -days 3650 \
  -nodes \
  -keyout ${DOMAIN}.key \
  -out ${DOMAIN}.crt \
  -extensions san \
  -config <(echo "[req]";
    echo distinguished_name=req;
    echo "[san]";
    echo subjectAltName=DNS:${DOMAIN},DNS:media.${DOMAIN}
    ) \
  -subj /CN=${DOMAIN}
