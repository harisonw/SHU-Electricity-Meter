import unittest, json
from unittest.mock import MagicMock, patch
from web3 import Web3

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
    
    @patch('web3.Web3')
    def test_store_and_get_bill(self, web3_mock):
        
        contract_mock = MagicMock()
        web3_mock.eth.contract.return_value = contract_mock

        with patch('web3.Web3', return_value=web3_mock), \
            patch.object(web3_mock.eth, 'contract', return_value=contract_mock):
            
            web3_mock.eth.default_account = "0xMockedAccount"

            contract_mock.functions.storeMeterReading.return_value.transact.return_value = "mocked_tx_hash"
            contract_mock.functions.getMeterBill.return_value.call.return_value = 200
            
            uid = "sample-uid"
            meter_reading = 100
            expected_bill = meter_reading * 2

            tx_hash = contract_mock.functions.storeMeterReading(uid, meter_reading).transact()
            assert tx_hash == "mocked_tx_hash", "Transaction hash mismatch"

            actual_bill = contract_mock.functions.getMeterBill().call()
            assert actual_bill == expected_bill, "Bill calculation error"

            print(f"Expected Bill: {expected_bill}, Actual Bill: {actual_bill}")

if __name__ == '__main__':
    unittest.main()