from fastapi import FastAPI
import pika
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("API")

# RabbitMQ connection
rabbit_host = 'rabbit'
rabbit_port = 5672
rabbit_queue = 'user_queue'

app = FastAPI()

items = {}


def establish_rabbit_connection(max_retries=10, retry_interval=5):
    for _ in range(max_retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host, rabbit_port))
            return connection
        except pika.exceptions.AMQPConnectionError:
            logger.warning("RabbitMQ connection failed. Retrying...")
            time.sleep(retry_interval)
    raise RuntimeError("Failed to establish RabbitMQ connection.")


@app.on_event('startup')
async def start_up():
    items['connection'] = establish_rabbit_connection()
    items['channel'] = items['connection'].channel()
    items['channel'].queue_declare(queue=rabbit_queue)


@app.post("/add_user/")
async def add_user(username: str):
    items['channel'].basic_publish(exchange='', routing_key='user_queue', body=username)
    return {"message": "User added to queue for processing"}
