#!/bin/bash

DOMAIN="quiz.xxxxx.org"

cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /etc/mosquitto/certs/
cp /etc/letsencrypt/live/$DOMAIN/cert.pem /etc/mosquitto/certs/
cp /etc/letsencrypt/live/$DOMAIN/chain.pem /etc/mosquitto/ca_certificates/


chown -R mosquitto:mosquitto /etc/mosquitto/certs
chown -R mosquitto:mosquitto /etc/mosquitto/ca_certificates

chmod 640 /etc/mosquitto/certs/*.pem
chmod 640 /etc/mosquitto/ca_certificates/*.pem


