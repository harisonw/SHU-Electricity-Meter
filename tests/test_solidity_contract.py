import unittest, json
from unittest.mock import MagicMock, patch
from web3 import Web3

#run test with = python -m unittest tests/test_solidity_contract.py
#all tests = python -m unittest discover -s tests

"""
unit tests for smart contract
includes positive and negative scenarios
"""

#mock abi to simulate contracts methods and i/o
mock_abi = [
    {
        "inputs": [
            {"internalType": "string", "name": "uid", "type": "string"},
            {"internalType": "uint256", "name": "mtr_reading", "type": "uint256"}
        ],
        "name": "storeMeterReading",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getMeterBill",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "constant": True,
        "type": "function"
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "constant": True,
        "type": "function"
    }
]

class test_solidity_contract(unittest.TestCase):
    #positive Test
    #storing and retrieving bill
    #mocking storage of data
    @patch('web3.Web3')
    def test_store_and_get_bill(self, web3_mock):
        #mock contract and web3 instance
        contract_mock = MagicMock()
        web3_mock.eth.contract.return_value = contract_mock

        with patch('web3.Web3', return_value=web3_mock), \
            patch.object(web3_mock.eth, 'contract', return_value=contract_mock):
            
            web3_mock.eth.default_account = "Account_Mock"
            
            uid = "uid"
            meter_reading = 20
            expected_bill = meter_reading * 2

            contract_mock.functions.storeMeterReading.return_value.transact.return_value = "mock_tx_hash"
            contract_mock.functions.getMeterBill.return_value.call.return_value = 40

            #storing
            tx_hash = contract_mock.functions.storeMeterReading(uid, meter_reading).transact()
            assert tx_hash == "mock_tx_hash", "transaction hash mismatch"

            #retrieving
            actual_bill = contract_mock.functions.getMeterBill().call()
            assert actual_bill == expected_bill, "bill calculation error"

            print(f"expected bill: {expected_bill}, actual bill: {actual_bill}")
         
    #positive test
    #retrieving contract owner adddress 
    @patch('web3.Web3')
    def test_get_owner(self, web3_mock):
        #mock contract and web3 instance
        contract_mock = MagicMock()
        web3_mock.eth.contract.return_value = contract_mock

        with patch('web3.Web3', return_value=web3_mock), \
            patch.object(web3_mock.eth, 'contract', return_value=contract_mock):
            
            mock_owner_address = "Owner_Mock"
            contract_mock.functions.owner.return_value.call.return_value = mock_owner_address

            owner_address = contract_mock.functions.owner().call()

            self.assertEqual(owner_address, mock_owner_address, "owner address mismatch")
            print(f"mocked owner address: {owner_address}")
            
    #negative test     
    #test invalid input handeling   
    @patch('web3.Web3')
    def test_store_meter_reading_invalid(self, web3_mock):
        #mock contract and web3 instance
        contract_mock = MagicMock()
        web3_mock.eth.contract.return_value = contract_mock

        with patch('web3.Web3', return_value=web3_mock), \
            patch.object(web3_mock.eth, 'contract', return_value=contract_mock):

            contract_mock.functions.storeMeterReading.return_value.transact.side_effect = Exception("transaction reverted")

            uid = "uid"
            meter_reading = -10 #invalid input

            with self.assertRaises(Exception) as context:
                contract_mock.functions.storeMeterReading(uid, meter_reading).transact()

            # Assertions
            self.assertIn("transaction reverted", str(context.exception), "expected transaction revert msg not found")
            print(f"caught expected exception: {context.exception}")
    
    #negative test
    #retrieving bill with no reading        
    @patch('web3.Web3')
    def test_get_empty_bill(self, web3_mock):
        #mock contract and web3 instance
        contract_mock = MagicMock()
        web3_mock.eth.contract.return_value = contract_mock

        with patch('web3.Web3', return_value=web3_mock), \
            patch.object(web3_mock.eth, 'contract', return_value=contract_mock):

            contract_mock.functions.getMeterBill.return_value.call.return_value = 0

            actual_bill = contract_mock.functions.getMeterBill().call()

            self.assertEqual(actual_bill, 0, "expected bill to be 0")
            print(f"bill with no readings: {actual_bill}")

if __name__ == '__main__':
    unittest.main()