from rabbit_mq import * 
from web3 import Web3
from parameters import CONTRACT_ABI, CONTRACT_ADDRESS, ACCOUNTS_DATA, BLOCKCHAIN_URL

if __name__ == '__main__': 
    w3 = Web3(Web3.HTTPProvider(BLOCKCHAIN_URL))
    example_address = Web3.to_checksum_address(list(ACCOUNTS_DATA['addresses'])[0])
    print(example_address)
    contract_instance = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    print(contract_instance.functions.set(100).transact({'from': example_address}))
    print(contract_instance.functions.get().call())