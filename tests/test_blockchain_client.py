import unittest, asyncio
from unittest.mock import Mock, MagicMock, patch
from client.blockchain_client import BlockchainStoreReading
#run test with = python -m unittest tests/test_blockchain_client.py

#TO DO: ERROR HANDLING AND DIFF METHODS

class TestClientBlockchain(unittest.TestCase):
    
    #test generate_reading returns a value thats part of the range
    def test_generate_reading(self):
        reading = BlockchainStoreReading.generate_reading()
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
    def test_store_reading_calls_storeMeterReading(self, mock_from_key, mock_uuid):
        mock_w3 = MagicMock()
        mock_contract = MagicMock()
        
        mock_uuid.return_value = 'test-uuid'
        mock_account = Mock()
        mock_account.address = 'Mahit_Address'
        mock_from_key.return_value = mock_account
        
        store_reading_obj = BlockchainStoreReading(
            private_key='test_key',
            w3=mock_w3,
            contract=mock_contract
        )
        
        with patch('client.blockchain_client.BlockchainStoreReading.generate_reading', return_value=5):
            asyncio.run(store_reading_obj.store_reading())
        
        mock_contract.functions.storeMeterReading.assert_called_once_with('test-uuid', 5)
        
        mock_contract.functions.getMeterBill().call.assert_called_once_with({"from": 'Mahit_Address'})
    
if __name__ == "__main__":
    unittest.main()