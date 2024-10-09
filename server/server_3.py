import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

queue = channel.queue_declare('rpc_queue')

rate_per_unit = 0.15 

def calculate_bill(meter_reading):
    bill_amount = meter_reading * rate_per_unit

    return bill_amount

def meter_request(ch, method, properties, body):
    payload = json.loads(body)
    meter_reading = payload['meter_reading']
    
    print("-------------------------------")
    print(f"Consuming meter data for {payload['user_email']}")
    print(f"Meter reading received {payload['meter_reading']}")
    print(f"Timestamp received {payload['timestamp']}")
    
    # Calculate new bill
    bill_update = calculate_bill(meter_reading)
    print(f"Calculated bill for {payload['user_email']}: {bill_update}")
    print("-------------------------------")
    # Send bill update to the client
    response = json.dumps(bill_update)

    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=response
    )

    # Send a acknoledge message back to Rabbit to say it was successfule
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Set up the consumer to listen for meter readings
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=meter_request)

print("---------Awaiting requests for meter readings----------")
channel.start_consuming()
