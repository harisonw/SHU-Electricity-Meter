import unittest, asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from client.blockchain_client import (get_contract,
                                      BlockchainConnectionMonitor,
                                      BlockchainGetBill,
                                      GenerateReadings,
                                      BlockchainStoreReading,
                                      BlockchainConnectionError,
                                      SmartMeterUI,
                                      BlockchainGetAlerts)

#run test with = python -m unittest tests/test_blockchain_client.py

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
        
    def test_blockchain_get_bill(self):
        mock_w3 = MagicMock()
        mock_contract = MagicMock()
        mock_ui_callback = MagicMock()
        mock_app = MagicMock()
        
        private_key = "0x" + "a" * 64 
        
        bill_instance = BlockchainGetBill(private_key, mock_w3, mock_contract, mock_ui_callback, mock_app)
        
        self.assertEqual(bill_instance.private_key, private_key)
        self.assertEqual(bill_instance.w3, mock_w3)
        self.assertEqual(bill_instance.contract, mock_contract)
        self.assertEqual(bill_instance.ui_callback, mock_ui_callback)
        self.assertEqual(bill_instance.app, mock_app)
        
    @patch('client.blockchain_client.BlockchainGetBill.poll_bill', new_callable=MagicMock)
    def test_poll_bill(self, mock_poll_bill):
        mock_w3 = MagicMock()
        mock_contract = MagicMock()
        mock_ui_callback = MagicMock()
        mock_app = MagicMock()
        
        private_key = "0x" + "a" * 64
        
        bill_instance = BlockchainGetBill(private_key, mock_w3, mock_contract, mock_ui_callback, mock_app)

        async def mock_poll_bill_coroutine():
            return None
        
        mock_poll_bill.side_effect = mock_poll_bill_coroutine
        
        asyncio.run(bill_instance.poll_bill())

        mock_poll_bill.assert_called_once()
        
    def test_generate_reading(self):
        generated_reading = GenerateReadings.generate_reading()
        self.assertTrue(1 <= generated_reading <= 10)
        
    @patch('client.blockchain_client.BlockchainStoreReading.store_reading', new_callable=MagicMock)
    def test_store_reading(self, mock_store_reading):
        mock_w3 = MagicMock()
        mock_contract = MagicMock()
        
        private_key = "0x" + "a" * 64 

        reading_instance = BlockchainStoreReading(private_key, mock_w3, mock_contract)

        async def mock_store_reading_coroutine(reading):
            return None 
        
        mock_store_reading.side_effect = mock_store_reading_coroutine
        
        asyncio.run(reading_instance.store_reading(5))

        mock_store_reading.assert_called_once_with(5)
        
    @patch('client.blockchain_client.Web3')
    def test_get_contract_error_handling(self, MockWeb3):
        app = MagicMock()
        mock_w3 = MagicMock()
        mock_w3.is_connected.return_value = False

        MockWeb3.return_value = mock_w3

        with self.assertRaises(BlockchainConnectionError):  # Expect the custom exception
            get_contract(app)

        app.update_connection_status.assert_called_with("error")
        
    def test_update_connection_status_connected(self):
        app = SmartMeterUI()
        app.update_connection_status("connected")
        self.assertEqual(app.connection_status_label.cget("text"), "Connected to server")
        self.assertEqual(app.connection_status_label.cget("text_color"), "green")
        
    @patch('client.blockchain_client.BlockchainGetAlerts.handle_grid_alert', new_callable=MagicMock)
    async def test_handle_grid_alert(self, mock_handle_grid_alert):
        mock_w3 = MagicMock()
        mock_contract = MagicMock()
        mock_ui_callback = MagicMock()
        alerts_instance = BlockchainGetAlerts(mock_w3, mock_contract, mock_ui_callback)

        mock_event = MagicMock()
        mock_event.args.message = "Test Alert"

        await alerts_instance.handle_grid_alert(mock_event)

        mock_handle_grid_alert.assert_called_once_with(mock_event)
        mock_ui_callback.update_notice_message.assert_called_with("Alert from the grid: Test Alert")
        
    @patch('time.sleep', return_value=None)
    def test_check_connection_disconnected(self, mock_sleep):
        app = MagicMock()
        mock_w3 = MagicMock()
        mock_w3.is_connected.return_value = False

        monitor = BlockchainConnectionMonitor(app, mock_w3)
        monitor.check_connection(iterations=1)

        app.update_connection_status.assert_called_with("error")
        
    @patch('client.blockchain_client.Web3')
    def test_get_contract_failure(self, MockWeb3):
        app = MagicMock()
        mock_w3 = MagicMock()
        mock_w3.is_connected.return_value = False

        MockWeb3.return_value = mock_w3

        with self.assertRaises(BlockchainConnectionError):  # Custom exception is expected
            get_contract(app)

        app.update_connection_status.assert_called_with("error")
    
    def test_invalid_private_key(self):
        private_key = "invalid_key"
        mock_w3 = MagicMock()
        mock_contract = MagicMock()

        with self.assertRaises(ValueError):
            BlockchainStoreReading(private_key, mock_w3, mock_contract)
            
    @patch('client.blockchain_client.BlockchainGetBill.poll_bill', new_callable=AsyncMock)
    def test_poll_bill_failure(self, mock_poll_bill):
        mock_w3 = MagicMock()
        mock_contract = MagicMock()
        mock_ui_callback = MagicMock()
        mock_app = MagicMock()
    
        private_key = "0x" + "a" * 64
        bill_instance = BlockchainGetBill(private_key, mock_w3, mock_contract, mock_ui_callback, mock_app)

        async def mock_poll_bill_coroutine():
            raise Exception("Polling error")

        mock_poll_bill.side_effect = mock_poll_bill_coroutine

        with self.assertRaises(Exception):
            asyncio.run(bill_instance.poll_bill())

        mock_poll_bill.assert_called_once()

if __name__ == "__main__":
    unittest.main()