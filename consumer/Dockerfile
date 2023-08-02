FROM python:3.11-slim

WORKDIR /app

COPY consumer/requirements.txt /app

RUN pip install -r requirements.txt

COPY consumer/ .

CMD ["python", "main.py"]
