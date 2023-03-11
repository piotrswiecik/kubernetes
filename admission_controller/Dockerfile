FROM python:3.11-slim-bullseye

WORKDIR /usr/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "controller:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile=/etc/tls/controller.pem", "--ssl-certfile=/etc/tls/controller.crt"]
