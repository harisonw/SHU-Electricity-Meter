import unittest, json, pika
from unittest.mock import patch, Mock
from server.server import calculate_price, on_request

class TestServer(unittest.TestCase):
    
    #resuable method
    def setUp(self):
        self.mock_connection = Mock()
        self.mock_channel = Mock()
        self.mock_connection.return_value.channel.return_value = self.mock_channel
        
    def test_calculate_price(self):
        meter_reading = 100
        expected_price = meter_reading * 0.22 
        self.assertEqual(calculate_price(meter_reading), expected_price)
        
        
if __name__ == '__main__':
    unittest.main()