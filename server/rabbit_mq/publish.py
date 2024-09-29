import pika
import json
import uuid
import time
from datetime import datetime
import random

# To run rabbit mq:
# 1. ran the cmd: docker-compose up
# 2. login using the following credentials guest/guest on the port http://localhost:15672

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(
    exchange='meter',
    exchange_type = 'direct'
)

meter = {
    'id': str(uuid.uuid4()),
    'user_email': 'shu@example.com',
    'meter_reading': random.randint(10, 100),
    'timestamp': datetime.now().isoformat()
}

channel.basic_publish(
    exchange='meter',
    routing_key='meter.notify',
    body=json.dumps(meter)
)
print('Sent notify message')

connection.close()