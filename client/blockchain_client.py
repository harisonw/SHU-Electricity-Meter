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
import threading
import time
from datetime import datetime
import asyncio
from web3 import Web3
import asyncio
from web3 import Web3
from client.parameters import CONTRACT_ABI, CONTRACT_ADDRESS, ACCOUNTS_DATA, BLOCKCHAIN_URL, first_address, first_private_key
from uuid import uuid4
from multiprocessing import Process
import time 
from eth_account import Account
#run python -m client.blockchain_client



def get_contract(): 
    try:
        w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))
        contract_instance = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
        return w3, contract_instance 
    except Exception as e: 
        raise e


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
            tx = self.contract.functions.storeMeterReading(uuid_.__str__(), reading).transact({"from": self.acc.address})
            
            print("Calling getMeterReadings()...")  #mahit debug
            
            bill = self.contract.functions.getMeterBill().call({"from": self.acc.address})
            meter_readings = self.contract.functions.getMeterReadings().call({"from": self.acc.address})
            print(f"Current Bill is: {bill}")
            print(f"Meter Readings: {meter_readings}")
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
            delay_interval = random.randint(2,5)
            await self.store_readings_obj.store_reading()
            await asyncio.sleep(delay_interval)

    def start_sending_readings(self):
        try: 
            asyncio.run(self.create_store_readings())
        except Exception as e: 
            raise e 

class BlockchainGetAlerts: 
    
    def __init__(self, w3, contract): 
        self.contract = contract 
        self.w3 = w3
    
    async def handle_grid_alert(self, event):
        print(f"Alert from the grid: {event.args.message}")

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

def process():
    while True: 
        print("test")
        time.sleep(1)   


if __name__ == "__main__":
    client_address = Web3.to_checksum_address(list(ACCOUNTS_DATA['addresses'])[0])    
    w3, contract = get_contract()
    alerts_obj = BlockchainGetAlerts(w3, contract)
    readings_obj = GenerateReadings(first_private_key, w3, contract)
    alert_thread = threading.Thread(target=alerts_obj.start_grid_alert_monitor)
    readings_thread = threading.Thread(target=readings_obj.start_sending_readings)
    alert_thread.start()
    readings_thread.start()