import json
import logging
import sys
from datetime import datetime, timedelta
import mongomock
import pika

PRICE_PER_KWH_GBP = 0.22





class MockMongoDB(): 

    def __init__(self): 
        self.client, self.db, self.collection = MockMongoDB.create_mock_db()

    @staticmethod
    def create_mock_db(): 
        client = mongomock.MongoClient()
        db = client['smart_meter_tool']
        collection = db['meter_readings']
        return client, db, collection 


    def insert_record(self, record): 
        try: 
            self.collection.insert_one(record)
            return True 
        except Exception as e: 
            raise e 

    def insert_records(self, record): 
        try: 
            self.collection.insert_many(record)
            return True 
        except Exception as e: 
            raise e 

    def find_records(self, query): 
        try:
            return self.collection.find(query)
        except Exception as e: 
            raise e
        
    def find_all(self): 
        try: 
            return self.collection.find()
        except Exception as e: 
            raise e 

def calculate_price(meter_reading):
    """
    Calculate the price based on the meter reading.

    Args:
        meter_reading (float): The meter reading value.

    Returns:
        float: The calculated price in GBP.
    """
    return meter_reading * PRICE_PER_KWH_GBP



db_instance = MockMongoDB()


def on_request(ch, method, properties, body):
    try:
        message = json.loads(body)
        meter_reading = float(message.get("meter_reading"))
    except Exception as e:
        logging.error("Invalid meter reading received: %s, Error: %s", body, str(e))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    logging.info("Received meter reading: %s", message)
    
    db_instance.insert_record(message)
    print(list(db_instance.find_all()))
    updated_price = calculate_price(meter_reading)

    TIMEOUT_SECONDS = 10
    try:
        timestamp_str = message.get("timestamp")
        # Convert the ISO timestamp string to a datetime object so we can add 10 seconds to it
        timestamp = datetime.fromisoformat(timestamp_str)
        if datetime.now() > timestamp + timedelta(seconds=10):
            logging.error("Request was stale, not sending response")
            ch.basic_ack(delivery_tag=method.delivery_tag)  # Remove the message
            return
    except Exception as e:
        logging.error(
            "Invalid timestamp received: %s, Error: %s", timestamp_str, str(e)
        )
        # Remove bad message from queue
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    # Send the response back using the reply_to and correlation_id
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id  # Include correlation ID in response
        ),
        body=str(updated_price),
    )

    ch.basic_ack(delivery_tag=method.delivery_tag)  # Remove the message


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        channel = connection.channel()
    # TODO: add retry logic if not able to connect? / reconnect logic if
    # connection is lost
    except pika.exceptions.AMQPError as e:
        logging.error("Error connecting to RabbitMQ: %s", e)
        sys.exit(1)

    # Declare the queue where the server will listen for meter readings
    channel.queue_declare(queue="meter_reading_queue", durable=True)
    channel.basic_qos(prefetch_count=1)

    # Set up the server to consume messages
    channel.basic_consume(queue="meter_reading_queue", on_message_callback=on_request)
    logging.info("Server started, waiting for meter readings...")
    channel.start_consuming()
