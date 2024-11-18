import time
from uuid import uuid4

from parameters import ACCOUNTS_DATA, BLOCKCHAIN_URL, CONTRACT_ABI, CONTRACT_ADDRESS
from web3 import Web3


def send_alert(contract):
    contract_instance.functions.sendGridAlert(
        "This is an alert from the blockchain"
    ).transact({"from": example_address})


if __name__ == "__main__":
    w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))
    example_address = Web3.to_checksum_address(list(ACCOUNTS_DATA["addresses"])[1])
    contract_instance = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    while True:
        send_alert(contract_instance)
        print("Sending Alert")
        time.sleep(2)
