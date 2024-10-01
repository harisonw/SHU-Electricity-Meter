"""
Reference: https://www.rabbitmq.com/tutorials/tutorial-six-python 
"""
import pika
import json
import uuid
import time
from datetime import datetime
import random

# To run rabbit mq:
# 1. ran the cmd: docker-compose up
# 2. login using the following credentials guest/guest on the port http://localhost:15672

class SmartMeter(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
            if self.corr_id == props.correlation_id:
                self.response = body

    #sends meter reading
    def call(self, meter_data):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        #publishes the rpc request to the server
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(meter_data)
        )

        # waits for the response
        while self.response is None:
            self.connection.process_data_events(time_limit=None)

        return self.response             


def generate_meter_reading():
    return {
        'id': str(uuid.uuid4()),
        'user_email': 'shu@example.com',
        'meter_reading': random.randint(10, 100),  # Simulated meter reading
        'timestamp': datetime.now().isoformat()
    }

meter_client = SmartMeter()

while True:
    # send meter reading at random intervals between 15 and 60
    interval = random.randint(15, 60)
    time.sleep(interval)
    
    meter_data = generate_meter_reading()

    print("-----------Sending meter data-----------")
    print(meter_data)

    response = meter_client.call(meter_data)

    print(f"Server Response Bill amount: {response.decode()}")
    print("----------------------------------------")