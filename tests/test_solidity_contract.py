import json #,os,
from web3 import Web3

ganache_url = "http://localhost:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))
assert web3.is_connected(), "Failed to connect to Ganache"

#TO DO: CHANGE PATH SO ITS NOT HARDCODED
#TO DO: MOCK

with open('C:/Users/MAHIT/Documents/SHU/Y3/Enterprise/SHU-Electricity-Meter/blockchain/build/contracts/ElectricityMeterReading.json') as f:
    contract_json = json.load(f)
    abi = contract_json['abi']          
    
#address from networks section in the json file
contract_address = "0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab"

#setup
contract = web3.eth.contract(address=contract_address, abi=abi)

# default account
web3.eth.default_account = web3.eth.accounts[0]

def test_store_and_get_bill():
    uid = "sample-uid"
    meter_reading = 50 
    tx_hash = contract.functions.storeMeterReading(uid, meter_reading).transact()
    web3.eth.wait_for_transaction_receipt(tx_hash) 

    #bill check
    expected_bill = meter_reading * 2  #
    actual_bill = contract.functions.getMeterBill().call()

    print(f"Expected Bill: {expected_bill}, Actual Bill: {actual_bill}")
    assert actual_bill == expected_bill, "Error in calculated bill"

test_store_and_get_bill()