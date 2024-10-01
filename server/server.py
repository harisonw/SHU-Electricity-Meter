from rabbit_mq import * 
from web3 import Web3


CONTRACT_ADDRESS = '0x88774E780A2c91e5745148bcd6Ca6c3708Bffd49'
CONTRACT_ABI = [
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_hero",
          "type": "string"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_hero",
          "type": "string"
        }
      ],
      "name": "setHero",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getHero",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    }
  ]
if __name__ == '__main__': 
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    contract_instance = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    print(contract_instance.functions.getHero().call())
    print(contract_instance.functions.setHero("Test").transact())
    print(contract_instance.functions.getHero().call())