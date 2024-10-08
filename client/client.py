import json
import random
import threading
import time
import uuid
from datetime import datetime

import customtkinter as ctk
import pika


class SmartMeterUI(ctk.CTk):
    """
    TODO: Add docstrings to classes and methods
    """

    def __init__(self):
        super().__init__()

        # Appearance and theme
        self.title("Smart Meter Interface")
        self.geometry("600x300")
        # Use native system dark / light mode
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Configure Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Server Connection status section
        self.grid_rowconfigure(1, weight=3)  # Main display
        self.grid_rowconfigure(2, weight=1)  # Outage Notice section

        # Define attributes
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

        self.time_label = ctk.CTkLabel(
            self.connection_status_frame,
            text="11:11",
            font=("Arial", 12),
            text_color="white",
        )
        self.time_label.pack(side="top", anchor="ne", padx=10)

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

        self.price_label = ctk.CTkLabel(
            self.middle_frame,
            text="£x.xx",
            font=("Arial", 36, "bold"),
            text_color="green",
        )
        self.price_label.pack(pady=(20, 5))

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

    def update_main_display(self, price, usage):
        self.price_label.configure(text=f"{price}")
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
        self.after(1000, self.update_time)  # Set to update every second


# TODO: Could do with decoupling this from the UI, perhaps by using a
# controller class?
class SmartMeterClient:
    def __init__(self):
        # TODO: Add error handling for connection failure, + retry logic (on another thread)
        # into SelectConnection instead of BlockingConnection
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters("localhost")
        )
        self.channel = self.connection.channel()

        # Set up a listener for direct reply-to using RPC (no need to declare a
        # queue)
        self.channel.basic_consume(
            queue="amq.rabbitmq.reply-to",
            on_message_callback=self.on_response,
            auto_ack=True,
        )

        self.response = None
        self.corr_id = None
        self.reading = 0.0  # TODO: Initial reading, need to populate this with a user's reading after user auth is implemented
        self.timeout_reading = None

    def on_response(self, _ch, _method, properties, body):
        if self.corr_id == properties.correlation_id:
            self.response = body

    @staticmethod
    def generate_meter_reading(reading_id, reading):
        return {
            "id": reading_id,
            "user_email": "shu@example.com",  # TODO: Replace with the user's email or ID
            "meter_reading": reading,
            "timestamp": datetime.now().isoformat(),
        }

    def send_meter_reading(self, reading_data):
        self.response = None
        self.corr_id = str(uuid.uuid4())  # Create a unique correlation ID

        # Publish the meter reading to the server
        self.channel.basic_publish(
            exchange="",
            routing_key="meter_reading_queue",  # Queue where the server listens
            properties=pika.BasicProperties(
                reply_to="amq.rabbitmq.reply-to",  # Use direct reply-to
                correlation_id=self.corr_id,  # Include the correlation ID
            ),
            body=json.dumps(reading_data),
        )  # TODO: Error handling

        start_time = time.time()  # Record the start time
        # Set the timeout duration in seconds, must be less than MIN_WAIT
        TIMEOUT_DURATION = 10

        # * Wait for the response, blocking until the response is received or a timeout, so must be ran in a separate thread
        while self.response is None:
            self.connection.process_data_events()
            if time.time() - start_time > TIMEOUT_DURATION:
                return "timeout"

        return self.response.decode("utf-8")  # Return the response as a string

    def update_meter_readings(self, app):
        MIN_INCREASE = 1.0  # TODO: Should these be moved to class attributes?
        MAX_INCREASE = 5.0
        # Generate a random increase in the reading
        increase = random.uniform(MIN_INCREASE, MAX_INCREASE)
        self.reading += increase  # Update the reading

        # Send the meter reading to the server and receiving an updated price
        reading_data = self.generate_meter_reading(1, self.reading)
        updated_price = self.send_meter_reading(reading_data)
        print(f"Price: {updated_price}")
        if self.timeout_reading and updated_price == "timeout":
            price_text = app.price_label.cget("text")
            app.update_main_display(price_text, f"{self.reading:.2f} kWh")
        elif updated_price == "timeout":
            app.update_connection_status("error")
            # show last know price @ last known reading
            original_price = app.price_label.cget("text")
            # part of logic to show last known price/reading
            self.timeout_reading = self.reading - increase
            if original_price in ("£x.xx", "£?.??"):
                app.update_main_display("£?.??", f"{self.reading:.2f} kWh")
            else:
                app.update_main_display(
                    f"£?.?? - was {original_price} @ {self.timeout_reading:.2f} kWh",
                    f"{self.reading:.2f} kWh",
                )

        else:
            self.timeout_reading = None
            app.update_connection_status("connected")
            # Convert the price to float and format to two decimal places
            updated_price = (
                f"{float(updated_price):.2f}"  # Format to two decimal places
            )

            # Update the main display
            app.update_main_display(f"£{updated_price}", f"{self.reading:.2f} kWh")

    def start_meter_updater(self, app):
        MIN_WAIT = 3  # Must be greater than TIMEOUT_DURATION
        MAX_WAIT = 5

        while True:
            wait_time = random.randint(MIN_WAIT, MAX_WAIT)
            print(f"Waiting for {wait_time} seconds...")
            time.sleep(wait_time)
            print("Done waiting")
            reading_thread = threading.Thread(
                target=self.update_meter_readings, args=(app,), daemon=True
            )
            reading_thread.start()


# Main app with mock data
if __name__ == "__main__":
    app = SmartMeterUI()

    # TODO: Simulate notice message, implement notice system
    app.after(
        5000,
        lambda: app.update_notice_message(
            "Alert: Possible electricity grid problem detected."
        ),
    )

    # Usage
    client = SmartMeterClient()

    # Start the meter reading updates in a separate thread
    reading_thread = threading.Thread(
        target=client.start_meter_updater, args=(app,), daemon=True
    )
    reading_thread.start()

    app.mainloop()
