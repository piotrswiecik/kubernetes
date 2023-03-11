#!/bin/bash

set -e

openssl genrsa -out pki/ca.key 2048 && \
openssl req -new -x509 -key pki/ca.key -out pki/ca.crt -config pki/ca.cfg && \
openssl genrsa -out pki/controller.pem 2048 && \
openssl req -new -key pki/controller.pem -subj "/CN=python-example-webhook.default.svc" -out pki/controller.csr && \
openssl x509 -req -in pki/controller.csr -extfile <(printf "subjectAltName=DNS:python-example-webhook.default.svc,DNS:python-example-webhook,DNS:python-example-webhook.default,DNS:python-example-webhook.default.svc.cluster.local") -CA pki/ca.crt -CAkey pki/ca.key -CAcreateserial -out pki/controller.crt

echo "CA_BUNDLE created"
sed -i s/caBundle.*$/caBundle:\ $(cat pki/ca.crt | base64 | tr -d "\n")/ admission.yaml
sed -i s/controller.crt.*$/controller.crt:\ $(cat pki/controller.crt | base64 | tr -d "\n")/ admission.yaml
sed -i s/controller.pem.*$/controller.pem:\ $(cat pki/controller.pem | base64 | tr -d "\n")/ admission.yaml