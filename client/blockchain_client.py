import asyncio
from web3 import Web3
from parameters import CONTRACT_ABI, CONTRACT_ADDRESS, ACCOUNTS_DATA, BLOCKCHAIN_URL
from uuid import uuid4
import threading
from multiprocessing import Process
import time 


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


if __name__ == '__main__': 
    w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))
    client_address = Web3.to_checksum_address(list(ACCOUNTS_DATA['addresses'])[0])    
    contract_instance = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    alerts_obj = BlockchainGetAlerts(contract_instance)
    alert_thread = threading.Thread(target=alerts_obj.start_grid_alert_monitor)
    alert_thread.start()
    process_thread = threading.Thread(target=process)
    process_thread.start()




