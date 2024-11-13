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
import threading 
import random
import time
from datetime import datetime
import asyncio
from web3 import Web3
from parameters import CONTRACT_ABI, CONTRACT_ADDRESS, ACCOUNTS_DATA, BLOCKCHAIN_URL, first_address, first_private_key, all_account_pairs
from uuid import uuid4
from multiprocessing import Process
import time 
from eth_account import Account
import json
import customtkinter as ctk


def get_contract(): 
    try:
        w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))
        contract_instance = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
        return w3, contract_instance 
    except Exception as e: 
        raise e

class BlockchainGetBill:
    def __init__(self, private_key, w3, contract, ui_callback): 
        self.w3 = w3
        self.private_key = private_key
        self.contract = contract 
        self.acc = Account.from_key(self.private_key)
        self.ui_callback = ui_callback
    
    async def poll_bill(self):
        while True:
            bill = self.contract.functions.getMeterBill().call({"from": self.acc.address})
            meter_readings = self.contract.functions.getMeterReadings.call({"from": self.acc.address})
            total_usage = sum(reading[1] for reading in meter_readings)
            print(bill,meter_readings)
            self.ui_callback.update_main_display(f"£{bill}", f"{total_usage} kWh") 
            #polling every 5 seconds
            await asyncio.sleep(5)

    def start_bill_monitor(self):
        try:
            asyncio.run(self.poll_bill())
        except KeyboardInterrupt:
            print("Stopping billing polling")
        

class BlockchainStoreReading: 

    def __init__(self, private_key, w3, contract): 
        try:
            self.private_key = private_key
            self.w3 = w3
            self.contract = contract 
            self.acc = Account.from_key(self.private_key)
        except Exception as e: 
            raise e 
        
    @staticmethod
    def generate_reading():
        random_reading = random.randint(1, 10)
        return random_reading
    
    async def store_reading(self): 
        try: 
            reading = BlockchainStoreReading.generate_reading()
            uuid_ = uuid4()
            #reading being stored with a transaction id
            tx = self.contract.functions.storeMeterReading(uuid_.__str__(), reading).transact({"from": self.acc.address})
        except Exception as e: 
            raise e 

class GenerateReadings: 

    def __init__(self, private_key, w3, contract):
        self.private_key = private_key
        self.w3 = w3
        self.contract = contract 
        self.store_readings_obj = BlockchainStoreReading(private_key, w3, contract)

    async def create_store_readings(self): 
        while True: 
            delay_interval = random.randint(5,10)
            await self.store_readings_obj.store_reading()
            await asyncio.sleep(delay_interval)

    def start_sending_readings(self):
        try: 
            asyncio.run(self.create_store_readings())
        except Exception as e: 
            raise e 

class BlockchainGetAlerts: 
    
    def __init__(self, w3, contract,ui_callback): 
        self.contract = contract 
        self.w3 = w3
        self.ui_callback = ui_callback
    
    async def handle_grid_alert(self, event):
        alert_message = f"Alert from the grid: {event.args.message}"
        print(alert_message)
        self.ui_callback.update_notice_message(alert_message)

    async def monitor_grid_alerts(self): 
        event_filter = self.contract.events.GridAlert.create_filter(from_block='latest')
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

if __name__ == "__main__":
    client_address = Web3.to_checksum_address(list(ACCOUNTS_DATA['addresses'])[0])    
    w3, contract = get_contract()
    app = SmartMeterUI()

    alerts_obj = BlockchainGetAlerts(w3, contract,app)
    readings_obj = GenerateReadings(first_private_key, w3, contract)
    bill_obj = BlockchainGetBill(first_private_key, w3, contract, app)

    alert_thread = threading.Thread(target=alerts_obj.start_grid_alert_monitor)
    readings_thread = threading.Thread(target=readings_obj.start_sending_readings)
    bill_thread = threading.Thread(target=bill_obj.start_bill_monitor)

    alert_thread.start()
    readings_thread.start()
    bill_thread.start()

    app.mainloop()
