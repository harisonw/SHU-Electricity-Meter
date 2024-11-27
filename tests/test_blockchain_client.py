import unittest, asyncio
from unittest.mock import MagicMock, patch
from client.blockchain_client import get_contract, BlockchainConnectionMonitor, BlockchainGetBill, SmartMeterUI

#run test with = python -m unittest tests/test_blockchain_client.py

#TO DO: ERROR HANDLING AND DIFF METHODS

class TestClientBlockchain(unittest.TestCase):
    
    @patch('client.blockchain_client.Web3')
    def test_get_contract_success(self, MockWeb3):
        app = MagicMock()
        
        mock_w3 = MagicMock()
        mock_w3.is_connected.return_value = True
        
        contract_mock = MagicMock()
        mock_w3.eth.contract.return_value = contract_mock
        
        MockWeb3.return_value = mock_w3
        
        w3, contract = get_contract(app)
        
        self.assertIsNotNone(w3)
        self.assertIsNotNone(contract)
        app.update_connection_status.assert_called_with("connected")
        
    @patch('client.blockchain_client.Web3')
    def test_check_connection_connected(self, MockWeb3):
        app = MagicMock()
        mock_w3 = MagicMock()
        mock_w3.is_connected.return_value = True 

        monitor = BlockchainConnectionMonitor(app, mock_w3)

        with patch('time.sleep', return_value=None):
            # Do not mock the method entirely, just run the first iteration
            monitor.check_connection()
            
        app.update_connection_status.assert_called_with("connected")

        

    
if __name__ == "__main__":
    unittest.main()