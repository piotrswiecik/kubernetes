FROM python:bullseye

WORKDIR /usr/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY .. .

CMD ["uvicorn", "cluster:app", "--host", "0.0.0.0", "--port", "8000"]