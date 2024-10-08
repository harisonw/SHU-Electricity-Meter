import json
import logging
import sys

import pika

PRICE_PER_KWH_GBP = 0.22


def calculate_price(meter_reading):
    """
    Calculate the price based on the meter reading.

    Args:
        meter_reading (float): The meter reading value.

    Returns:
        float: The calculated price in GBP.
    """
    return meter_reading * PRICE_PER_KWH_GBP


def on_request(ch, method, properties, body):
    """
    TODO: Add docstring
    """
    try:
        message = json.loads(body)
        meter_reading = float(message.get("meter_reading"))
    except (ValueError, json.JSONDecodeError) as e:
        logging.error("Invalid meter reading received: %s, Error: %s", body, str(e))
        # Remove bad message from queue
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    logging.info("Received meter reading: %s", message)

    updated_price = calculate_price(meter_reading)

    # TODO: Integrate with the blockchain

    # TODO: Don't bother to send response back if time is past the request.timestamp + TIMEOUT_DURATION (10secs)
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
