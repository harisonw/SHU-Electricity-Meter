# client send and polls from the block chain smart contract
"""
Connect to the Blockchain:
    Establish a connection to the Ganache blockchain using web3.py.
Access the Smart Contract:
    Load the contract's ABI (Application Binary Interface) and address.
    Create a contract instance in your client application.
Set Up Event Listeners:
    Subscribe to the GridAlert event emitted by the smart contract.
Handle Incoming Alerts:
    Define a callback function to process and display the alert messages when events are received.
Integrate with Client Logic:
    Incorporate event listening into the main execution flow of client.py.

Reference link: https://medium.com/@0xCodeCharmer/interacting-with-smart-contracts-with-web3-py-9fee1a4274ec
"""
import asyncio
import json
import logging
import random
import sys
import threading
import time
from datetime import datetime
from multiprocessing import Process
from uuid import uuid4

import customtkinter as ctk
from eth_account import Account
from parameters import (
    ACCOUNTS_DATA,
    BLOCKCHAIN_URL,
    CONTRACT_ABI,
    CONTRACT_ADDRESS,
)
from web3 import Web3



    

def get_contract(app):
    try:
        w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL, request_kwargs={"timeout": 60}))
        if not w3.is_connected:
            app.update_connection_status("error")
            return None, None
        contract_instance = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
        app.update_connection_status("connected")
        return w3, contract_instance
    except Exception as e:
        app.update_connection_status("error")
        raise e


class BlockchainConnectionMonitor:
    def __init__(self, app, w3):
        self.app = app
        self.w3 = w3

    def check_connection(self):
        while True:
            if not self.w3.is_connected():
                self.app.update_connection_status("error")
            else:
                self.app.update_connection_status("connected")
            time.sleep(5)


class BlockchainGetBill:
    def __init__(self, private_key, w3, contract, ui_callback):
        self.w3 = w3
        self.private_key = private_key
        self.contract = contract
        self.acc = Account.from_key(self.private_key)
        self.ui_callback = ui_callback

    async def poll_bill(self):
        total_usage = None
        while True:
            displayed_usage_text = app.usage_label.cget("text")
            try:
                displayed_usage = (
                    displayed_usage_text.split(": ")[1].strip().split(" ")[0]
                )
                if displayed_usage == "xx.xx":
                    displayed_usage = None
                else:
                    displayed_usage = float(displayed_usage)
            except Exception as e:
                logging.error(e)

            if total_usage == None:
                bill = (
                    self.contract.functions.getMeterBill().call(
                        {"from": self.acc.address}
                    )
                    / 1000
                )
                meter_readings = self.contract.functions.getMeterReadings.call(
                    {"from": self.acc.address}
                )
                total_usage = sum(reading[1] for reading in meter_readings)/1000
                logging.info(
                    "Received Initial Bill: £%s @ Meter reading: %s kWh",
                    bill,
                    total_usage,
                )
                self.ui_callback.update_main_display(
                    f"£{bill:.2f}", f"{total_usage:.2f} kWh"
                )
            elif total_usage != displayed_usage:
                # Await for the blockchain to update the usage
                while total_usage != displayed_usage:
                    logging.info(
                        "Total usage: %s, Displayed usage: %s",
                        total_usage,
                        displayed_usage,
                    )
                    meter_readings = self.contract.functions.getMeterReadings.call(
                        {"from": self.acc.address}
                    )
                    total_usage = sum(reading[1] for reading in meter_readings)
                    await asyncio.sleep(0.01)

                bill = (
                    self.contract.functions.getMeterBill().call(
                        {"from": self.acc.address}
                    )
                    / 1000
                )
                logging.info(
                    "Received New Bill: £%s @ Meter reading: %s kWh", bill, total_usage
                )
                self.ui_callback.update_main_display(
                    f"£{bill:.2f}", f"{total_usage:.2f} kWh"
                )

            # polling every 0.1 seconds
            await asyncio.sleep(0.1)

    def start_bill_monitor(self):
        try:
            asyncio.run(self.poll_bill())
        except KeyboardInterrupt:
            logging.info("Stopping billing polling")


class BlockchainStoreReading:

    def __init__(self, private_key, w3, contract):
        try:
            self.private_key = private_key
            self.w3 = w3
            self.contract = contract
            self.acc = Account.from_key(self.private_key)
        except Exception as e:
            raise e

    async def store_reading(self, reading):
        try:
            reading = (
                reading * 1000
            )  # Using Scaled Interger to represent decimal reading
            uuid_ = uuid4()
            # reading being stored with a transaction id
            tx = self.contract.functions.storeMeterReading(
                uuid_.__str__(), reading
            ).transact({"from": self.acc.address})
            logging.info("Stored reading: %s with tx: %s", reading, tx.hex())
        except Exception as e:
            logging.error(str(e))
            raise e 


class GenerateReadings:

    def __init__(self, private_key, w3, contract, app):
        self.private_key = private_key
        self.w3 = w3
        self.contract = contract
        self.store_readings_obj = BlockchainStoreReading(private_key, w3, contract)
        self.app = app
        self.backlogs = []

    @staticmethod
    def generate_reading():
        random_reading = random.randint(1, 10)  # TODO: Change to decimal reading
        return random_reading

    async def reading_generator(self):
        MIN_WAIT = 1  # TODO: Change back to 15 and 60 when all testing done
        MAX_WAIT = 2

        while True:

            delay_interval = random.randint(MIN_WAIT, MAX_WAIT)
            await asyncio.sleep(delay_interval)

            reading = self.generate_reading()
            logging.info("Generated reading: %s", reading)

            # Populate the UI with new reading incase of connection loss with the blockchain
            previous_price_text = app.price_label.cget("text")
            previous_usage_text = app.usage_label.cget("text")
            try:
                previous_usage = float(
                    previous_usage_text.split(": ")[1].strip().split(" ")[0]
                )
                new_usage = previous_usage + reading
                app.update_main_display(previous_price_text, f"{new_usage:.2f} kWh")
            except ValueError:
                pass
                
            try:
                asyncio.create_task(self.store_readings_obj.store_reading(reading))
                logging.info(self.backlogs)
                asyncio.create_task(self.clear_backlogs())
            except Exception as e: 
                self.backlogs.append(e)

    async def clear_backlogs(self): 
        if len(self.backlogs)>1: 
            for index in range(self.backlogs): 
                try: 
                    asyncio.create_task(self.store_readings_obj.store_reading(self.backlogs[index]))
                    record = self.backlogs.pop(index)
                    logging.info("Stored reading from backlog: %s ", str(record))
                except Exception as e: 
                    print(str(e))

    def start_reading_generator(self):
        try:
            asyncio.run(self.reading_generator())
        except Exception as e:
            raise e


def generate_existing_readings():
    initial_set = []
    for _ in range(12):
        reading = GenerateReadings.generate_reading()
        initial_set.append({"uuid_": str(uuid4()), "reading":reading})
    return initial_set

def store_initial_set(initial_set, **blockchain_args):
    store_readings_obj = BlockchainStoreReading(**blockchain_args)
    for record in initial_set: 
        store_readings_obj.store_reading(record)
        

class BlockchainGetAlerts:

    def __init__(self, w3, contract, ui_callback):
        self.contract = contract
        self.w3 = w3
        self.ui_callback = ui_callback

    async def handle_grid_alert(self, event):
        alert_message = f"Alert from the grid: {event.args.message}"
        logging.info(alert_message)
        self.ui_callback.update_notice_message(alert_message)

    async def monitor_grid_alerts(self):
        event_filter = self.contract.events.GridAlert.create_filter(from_block="latest")
        while True:
            for event in event_filter.get_new_entries():
                await self.handle_grid_alert(event)
            await asyncio.sleep(2)

    def start_grid_alert_monitor(self):
        try:
            asyncio.run(self.monitor_grid_alerts())
        except KeyboardInterrupt:
            pass


class SmartMeterUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Appearance and theme
        self.title("Smart Meter Interface")
        self.geometry("650x300")
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
            self.price_label.configure(text_color="green")
            self.is_connected = True
        if status == "error":
            self.connection_status_label.configure(
                text="Error: Failed to connect to server. Retrying...",
                text_color="gold",
            )
            self.price_label.configure(text_color="gold")

    def update_main_display(self, price, usage):
        self.price_label.configure(text=f"{price}")
        self.usage_label.configure(text=f"Used so far today: {usage}")

    def update_main_usage(self, usage):
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    client_number = int(sys.argv[1])
    private_key = list(ACCOUNTS_DATA["private_keys"].values())[client_number]
    app = SmartMeterUI()
    w3, contract = get_contract(app)

    initial_set = generate_existing_readings()
    print(initial_set)
    store_initial_set(initial_set, private_key=private_key, w3=w3, contract=contract)

    if w3 and contract:
        alerts_obj = BlockchainGetAlerts(w3, contract, app)
        readings_obj = GenerateReadings(private_key, w3, contract, app)
        bill_obj = BlockchainGetBill(private_key, w3, contract, app)
        connection_monitor = BlockchainConnectionMonitor(app, w3)

        alert_thread = threading.Thread(
            target=alerts_obj.start_grid_alert_monitor, daemon=True
        )
        readings_thread = threading.Thread(
            target=readings_obj.start_reading_generator, daemon=True
        )
        bill_thread = threading.Thread(target=bill_obj.start_bill_monitor, daemon=True)
        connection_monitor_thread = threading.Thread(
            target=connection_monitor.check_connection, daemon=True
        )

        alert_thread.start()
        readings_thread.start()
        bill_thread.start()
        connection_monitor_thread.start()

    app.mainloop()
