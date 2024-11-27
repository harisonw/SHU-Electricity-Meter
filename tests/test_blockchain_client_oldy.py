import unittest, asyncio
from unittest.mock import Mock, MagicMock, patch
from client.blockchain_client import BlockchainStoreReading, GenerateReadings

#run test with = python -m unittest tests/test_blockchain_client.py

#TO DO: ERROR HANDLING AND DIFF METHODS

class TestClientBlockchain(unittest.TestCase):
    
    #test generate_reading returns a value thats part of the range
    def test_generate_reading(self):
        reading = GenerateReadings.generate_reading()
        self.assertTrue(1 <= reading <= 10, "Reading should be between 1 and 10")
        
    #test to check if setup of blockchainStoreReading is right
    @patch('client.blockchain_client.Account.from_key')
    def test_blockchainStoreReadingSetUp(self, mock_from_key):
        mock_account = Mock()
        mock_account.address = 'Mahit'
        mock_from_key.return_value = mock_account

        #instance
        store_reading_obj = BlockchainStoreReading(
            private_key='test_key',
            w3=Mock(),
            contract=Mock()
        )

        self.assertEqual(store_reading_obj.acc.address, 'Mahit')
        mock_from_key.assert_called_once_with('test_key')
      
    #test to check store_reading method calls blockchain contract functions
    @patch('client.blockchain_client.uuid4')
    @patch('client.blockchain_client.Account.from_key')
    @patch('client.blockchain_client.GenerateReadings.generate_reading', return_value=5)
    @patch('client.blockchain_client.Web3.eth.contract')
    def test_store_reading_calls_storeMeterReading(self, mock_generate_reading, mock_from_key, mock_uuid):
        mock_w3 = MagicMock()
        mock_contract = MagicMock()
        
        fake_tx = MagicMock()
        fake_tx.hex.return_value = '0x123abc'
        
        mock_contract.functions.storeMeterReading.return_value.transact.return_value = fake_tx
        mock_contract.functions.getMeterBill.return_value.call.return_value = 1000  #fake return
        
        mock_uuid.return_value = 'test-uuid'
        mock_account = Mock()
        mock_account.address = 'Mahit_Address'
        mock_from_key.return_value = mock_account
        
        store_reading_obj = BlockchainStoreReading(
            private_key='test_key',
            w3=mock_w3,
            contract=mock_contract
        )
        
        asyncio.run(store_reading_obj.store_reading(5))
        
        mock_contract.functions.storeMeterReading.assert_called_once_with('test-uuid', 5000)
        
        mock_contract.functions.getMeterBill().call.assert_called_once_with({"from": 'Mahit_Address'})
    
if __name__ == "__main__":
    unittest.main()
    
    """
        @patch('client.blockchain_client.Web3')
    def test_get_contract_error(self, MockWeb3):
        app = MagicMock()
        
        mock_w3 = MagicMock()
        mock_w3.is_connected.return_value = False
        
        MockWeb3.return_value = mock_w3
        
        w3, contract = get_contract(app)
        
        self.assertIsNone(w3)
        self.assertIsNone(contract)
        app.update_connection_status.assert_called_with("error")
    """
    
    """
        @patch("web3.eth.Contract") 
    @patch("client.blockchain_client.SmartMeterUI")
    @patch('asyncio.sleep', return_value=None)
    def test_poll_bill_initial_usage(self, mock_sleep, MockUI, MockContract):
        mock_app = MockUI.return_value
        
        mock_app.usage_label = MagicMock()
        mock_app.usage_label.cget.return_value = "Used so far today: xx.xx kWh"
        
        mock_contract = MockContract.return_value
        mock_contract.functions.getMeterBill().call.return_value = 5000 
        mock_contract.functions.getMeterReadings.call.return_value = [
            ("reading_id_1", 10), 
            ("reading_id_2", 15),
        ]
        
        private_key = "0x4c0883a69102937d6231471b5dbb62b9c3d0fba5365e589c0e3f107d7f6c01f0" 
        bill_monitor = BlockchainGetBill(private_key, "mock_w3", mock_contract, mock_app, mock_app)
        
        max_iterations = 2
        iteration_count = 0
        
        async def run_test():
            nonlocal iteration_count
            # Mock the polling loop to run a limited number of iterations
            while iteration_count < max_iterations:
                await bill_monitor.poll_bill()
                iteration_count += 1
        
        asyncio.run(run_test())
        
        mock_app.update_main_display.assert_called_with("£50.00", "25.00 kWh")
        
        mock_contract.functions.getMeterBill().call.assert_called_once()
        mock_contract.functions.getMeterReadings.call.assert_called_once()
    """