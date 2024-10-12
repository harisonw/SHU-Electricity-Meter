import pika
import json

rate_per_unit = 0.15

def calculate_bill(meter_reading):
    #validation to handle negative readings
    if meter_reading < 0:
        print("Error: Meter reading cannot be negative")
        raise ValueError("Meter reading cannot be negative")
    bill_amount = meter_reading * rate_per_unit
    return bill_amount

def meter_request(ch, method, properties, body):
    payload = json.loads(body)
    meter_reading = payload['meter_reading']
    
    print("-------------------------------")
    print(f"Consuming meter data for {payload['user_email']}")
    print(f"Meter reading received: {meter_reading}")
    print(f"Timestamp received: {payload['timestamp']}")
    
    #calc new bill
    bill_update = calculate_bill(meter_reading)
    print(f"Calculated bill for {payload['user_email']}: {bill_update}")
    print("-------------------------------")
    
    #send bill to update client
    response = json.dumps(float(bill_update))

    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=response
    )

    #send a acknoledge message back to Rabbit to say it was successfulll
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='rpc_queue')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='rpc_queue', on_message_callback=meter_request)

    print("--------- Awaiting requests for meter readings ---------")
    channel.start_consuming()

if __name__ == "__main__":
    main()
