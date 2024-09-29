import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

queue = channel.queue_declare('meter_notify')
queue_name = queue.method.queue

channel.queue_bind(
    exchange='meter',
    queue = queue_name,
    routing_key='meter.notify' 
)

def callback(ch, method, properties, body):
    payload = json.loads(body)
    print('--START--')
    print(f"Consuming meter data for {payload['user_email']}")
    print(payload['meter_reading'])
    print(payload['timestamp'])
    print('--DONE YAYAY--')
    # Send a acknoledge message back to Rabbit to say it was successfule
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(on_message_callback=callback, queue = queue_name)

print('Waiting for meter notify messages...')

channel.start_consuming()
