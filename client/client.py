"""
Reference: https://www.rabbitmq.com/tutorials/tutorial-six-python 
"""
import pika
import json
import uuid
import time
from datetime import datetime
import random
import threading

import customtkinter as ctk

# To run rabbit mq:
# 1. ran the cmd: docker-compose up
# 2. login using the following credentials guest/guest on the port http://localhost:15672

class SmartMeterClient:
    def __init__(self, app):
        self.connection = None
        self.channel = None
        self.response = None
        self.corr_id = None
        self.reading = 0.0
        self.reading_id = str(uuid.uuid4())
        self.user_email = str(uuid.uuid4()) + "@gmail.com"
        # update UI
        self.app = app
        self.connected = False

        # check connection to the server initially and periodically
        self.connect_to_server()
        connection_thread = threading.Thread(target=self.check_connection_status, daemon=True)
        connection_thread.start() 

    def connect_to_server(self):
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            self.channel = self.connection.channel()

            self.channel.basic_consume(
                queue="amq.rabbitmq.reply-to",
                on_message_callback=self.on_response,
                auto_ack=True
            )

            self.connected = True
            self.app.update_connection_status("connected")

        except pika.exceptions.AMQPConnectionError as e:
            print(f"Error connecting to RabbitMQ: {e}")
            self.app.update_connection_status("error")

    def check_connection_status(self):
        while True:
            # if connection is set to none or connection has been closed then status changed to error
            if self.connection is None or self.connection.is_closed:
                self.connected = False
                self.app.update_connection_status("error")
                # and try to reconnect
                self.connect_to_server()
            else:
                self.connected = True
                
            time.sleep(5)

    def close(self):
        if self.is_connected():
            self.connection.close()
            self.connection = None
            print("Closed RabbitMQ connection")

    def on_response(self, ch, method, props, body):
            if self.corr_id == props.correlation_id:
                self.response = body

    def generate_meter_reading(self):
        return {
            "id": self.reading_id,
            "user_email": self.user_email,
            "meter_reading": self.reading,
            "timestamp": datetime.now().isoformat(),
        }

    #sends meter reading
    def send_meter_reading(self, reading_data):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        #publishes the rpc request to the server
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to="amq.rabbitmq.reply-to",
                correlation_id=self.corr_id,
            ),
            body=json.dumps(reading_data)
        )   

        # timeout if no response from server
        start_time = time.time()
        timeout = 10

        # waits for the response
        while self.response is None:
            self.connection.process_data_events()
            # if the difference between now time and starting time is greater than timeout (10 sec) it will return none and loop out
            if time.time() - start_time > timeout:
                print("Time out: No response!")
                return None
        return self.response      
    
    def update_meter_readings(self, app):
        # random increase in reading
        self.reading += random.uniform(1.0, 5.0)

        reading_data = self.generate_meter_reading()
        print(f"Meter reading sent: {reading_data} kWh")
        updated_price = self.send_meter_reading(reading_data)

        #decode from bytes to string and then float for correct format
        updated_price = updated_price.decode()  
        updated_price = float(updated_price) 

        print(f"Updated Price: £{updated_price:.2f}")
        app.update_main_display(f"£{updated_price:.2f}", f"{self.reading:.2f} kWh")

    def start_meter_updater(self, app):
        while True:
            wait_time = random.randint(15, 60)
            print(f"Waiting {wait_time} seconds to send...")
            time.sleep(wait_time)
            self.update_meter_readings(app)


class SmartMeterUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Appearance and theme
        self.title("Smart Meter Interface")
        self.geometry("600x300")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Configure Grid layout
        self.grid_columnconfigure(0, weight=1)  # Create a single column
        self.grid_rowconfigure(0, weight=1)  # Server Connection status section
        self.grid_rowconfigure(1, weight=3)  # Main display
        self.grid_rowconfigure(2, weight=1)  # Outage Notice section

        # UI elements initialization
        self.connection_status_frame = None
        self.connection_status_label = None
        self.time_label = None
        self.middle_frame = None
        self.price_label = None
        self.usage_label = None
        self.notice_frame = None
        self.notice_label = None

        self.create_widgets()

    # Create UI components
    def create_widgets(self):
        self.create_connection_status()
        self.create_main_display()
        self.create_notice_section()
        self.update_time()

    def create_connection_status(self):
        self.connection_status_frame = ctk.CTkFrame(
            self, corner_radius=10, fg_color="grey17"
        )
        self.connection_status_frame.grid(
            row=0, column=0, padx=20, pady=10, sticky="nsew"
        )

        # Time label
        self.time_label = ctk.CTkLabel(
            self.connection_status_frame,
            text="11:11",
            font=("Arial", 12),
            text_color="white",
        )
        self.time_label.pack(side="top", anchor="ne", padx=10)

        # Connection status label
        self.connection_status_label = ctk.CTkLabel(
            self.connection_status_frame,
            text="Connecting to server...",
            font=("Arial", 14, "bold"),
            text_color="white",
        )
        self.connection_status_label.pack(pady=(0, 10))

    def create_main_display(self):
        self.middle_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="grey12")
        self.middle_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.amount_label = ctk.CTkLabel(
            self.middle_frame,
            text="£x.xx",
            font=("Arial", 36, "bold"),
            text_color="green",
        )
        self.amount_label.pack(pady=(20, 5))

        self.usage_label = ctk.CTkLabel(
            self.middle_frame,
            text="Used so far today: xx.xx kWh",
            font=("Arial", 16),
            text_color="white",
        )
        self.usage_label.pack(pady=(5, 0))

    def create_notice_section(self):
        self.notice_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="grey17")
        self.notice_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        self.notice_label = ctk.CTkLabel(
            self.notice_frame,
            text="No current notices",
            font=("Arial", 14, "bold"),
            text_color="white",
        )
        self.notice_label.pack(pady=10)

    def update_connection_status(self, status):
        if status == "connected":
            self.connection_status_label.configure(
                text="Connected to server", text_color="green"
            )
        if status == "error":
            self.connection_status_label.configure(
                text="Error: Failed to connect to server. Retrying...",
                text_color="gold",
            )

    def update_main_display(self, amount, usage):
        self.amount_label.configure(text=amount)
        self.usage_label.configure(text=f"Used so far today: {usage}")

    def update_notice_message(self, message):
        if message == "":
            message = "No current notices"
            self.notice_label.configure(text=message, text_color="grey")
        else:
            self.notice_label.configure(text=message, text_color="red")

    def update_time(self):
        current_time = datetime.now().strftime("%H:%M")
        self.time_label.configure(text=current_time)  # Update the time label
        self.after(1000, self.update_time)  # Update every second


if __name__ == "__main__":
    app = SmartMeterUI()

    client = SmartMeterClient(app)

    #start meter reading updates in a separate thread
    reading_thread = threading.Thread(target=client.start_meter_updater, args=(app,), daemon=True)
    reading_thread.start()

    app.mainloop()