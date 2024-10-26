from rabbit_mq import * 
from web3 import Web3
from parameters import CONTRACT_ABI, CONTRACT_ADDRESS, ACCOUNTS_DATA, BLOCKCHAIN_URL
from uuid import uuid4
import time 

def send_alert(contract): 
    contract_instance.functions.sendGridAlert("This is an alert from the blockchain").transact({'from': example_address}) 


if __name__ == '__main__': 
    w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))
    example_address = Web3.to_checksum_address(list(ACCOUNTS_DATA['addresses'])[1])
    contract_instance = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    while True: 
        send_alert(contract_instance)
        time.sleep(2)