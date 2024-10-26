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
from server.parameters import BLOCKCHAIN_URL, CONTRACT_ADDRESS, CONTRACT_ABI, first_address, first_private_key
import asyncio
from web3 import Web3
from parameters import CONTRACT_ABI, CONTRACT_ADDRESS, ACCOUNTS_DATA, BLOCKCHAIN_URL
from uuid import uuid4
from multiprocessing import Process
import time 



# connect to ganache and then check if its connected
web3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))
print(web3.isConnected())

# creating a contract object using the contract address and abi (json representation of methods and arguments)
contract = web3.eth.contract(address = CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# TO DOOOOOOOOO 
# maybe add this to the paranthesis and make it dynamic rather than first key
account = web3.eth.account.privateKeyToAccount(first_private_key)

def generate_reading():
    random_reading = random.randint(1, 100)
    return random_reading
 
def blockchain_get_reading():
    getReading=contract.functions.getMeterReadings().call()
    print(getReading)

def blockchain_store_reading():
    random_reading = generate_reading()
    timestamp_of_reading = datetime.now().isoformat()

    # when storing anything on smart contract it's a transaction as it changes the state of block chain
    transaction = contract.functions.set(random_reading).buildTransaction({
        # nonce: client address using private key
        'nonce': web3.eth.getTransactionCount(account.address),
        'from': account.address,
        'gas': 20000000,
        'gasPrice': web3.toWei('1', 'gwei')
    })
    # sign this transaction using private key and send it to the network
    signed_txn = web3.eth.account.signTransaction(transaction, account.privateKey)
    web3.eth.sendRawTransaction(signed_txn.rawTransaction)

def blockchain_get_bill():
    """
    TO DOOOOOOOOO
    need to create a new function within smart contract that calculates the bill and returns it
    """
    getBillResult=contract.functions.NEEDFUNCTION_NAME_HERE().call()
    print(getBillResult)

def listening_to_alerts():
    pass




class GenerateReading: 
    pass 

class BlockchainStoreReading: 
    pass 


class BlockchainGetBill: 
    pass 


class BlockchainGetAlerts: 
    
    def __init__(self, contract): 
        self.contract = contract 
    
    async def handle_grid_alert(self, event):
        print(event)

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
    w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))
    client_address = Web3.to_checksum_address(list(ACCOUNTS_DATA['addresses'])[0])    
    contract_instance = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    alerts_obj = BlockchainGetAlerts(contract_instance)
    alert_thread = threading.Thread(target=alerts_obj.start_grid_alert_monitor)
    alert_thread.start()
    process_thread = threading.Thread(target=process)
    process_thread.start()

    try:
        while True:
            blockchain_store_reading()
            time_to_wait = random.randint(15, 60)
            time.sleep(time_to_wait)
    except KeyboardInterrupt:
        print("Client stopped")