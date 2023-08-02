import pika
import pymongo
import time
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CONSUMER")

# RabbitMQ connection
rabbit_host = 'rabbit'
rabbit_port = 5672
rabbit_queue = 'user_queue'

# MongoDB connection
mongo_client = pymongo.MongoClient('mongodb://db:27017/')
db = mongo_client['user_db']
users_collection = db['users']


def establish_rabbit_connection(max_retries=10, retry_interval=5):
    for _ in range(max_retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host, rabbit_port))
            return connection
        except pika.exceptions.AMQPConnectionError:
            logger.warning("RabbitMQ connection failed. Retrying...")
            time.sleep(retry_interval)
    raise RuntimeError("Failed to establish RabbitMQ connection.")


def callback(ch, method, properties, body):
    time.sleep(10)
    username = body.decode()
    users_collection.insert_one({'username': username})
    logger.info(f"Recorded user: {username}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_user_queue():
    connection = establish_rabbit_connection()
    channel = connection.channel()
    channel.queue_declare(queue=rabbit_queue)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='user_queue', on_message_callback=callback)

    channel.start_consuming()


if __name__ == "__main__":
    consume_user_queue()
