import unittest, json, pika, datetime
from unittest.mock import patch, Mock
from server.server import calculate_price, on_request
from datetime import datetime, timedelta

#TODO: comments + maybe more tests?

class TestServer(unittest.TestCase):
    """
    unit tests to test server functionality
    tests for calculate_price and on_request
    """
    #resuable method
    def setUp(self):
        self.mock_connection = Mock()
        self.mock_channel = Mock()
        self.mock_connection.return_value.channel.return_value = self.mock_channel
        
    def test_calculate_price(self):
        meter_reading = 20
        expected_price = meter_reading * 0.22 
        self.assertEqual(calculate_price(meter_reading), expected_price)
        
    def test_calcualte_price_negative(self):
        meter_reading = -20
        expected_price= meter_reading * 0.22
        self.assertEqual(calculate_price(meter_reading), expected_price)
    
    @patch('pika.BlockingConnection')    
    def test_on_request(self, mock_connection):
        mock_method = Mock()
        mock_properties = Mock()
        mock_properties.reply_to = 'reply_queue'
        mock_properties.correlation_id = 'mahit123'
        
        payload = {
            'user_email': 'mahit@shu.com',
            'meter_reading': 20,
            'timestamp': datetime.now().isoformat() 
        }
        body = json.dumps(payload)
        
        on_request(self.mock_channel, mock_method, mock_properties, body)
        
        expected_price = calculate_price(20)
        
        self.mock_channel.basic_publish.assert_called_once_with(
            exchange='',
            routing_key='reply_queue',
            properties=pika.BasicProperties(correlation_id='mahit123'),
            body=str(expected_price)
        )
        self.mock_channel.basic_ack.assert_called_once_with(delivery_tag=mock_method.delivery_tag)
        
    @patch('pika.BlockingConnection')    
    def test_on_request_invalid_reading(self, mock_connection):
        mock_method = Mock()
        mock_properties = Mock()
        mock_properties.reply_to = 'reply_queue'
        mock_properties.correlation_id = 'mahit123'
        
        payload = {
            'user_email': 'mahit@shu.com',
            'meter_reading': 'invalid',
            'timestamp': datetime.now().isoformat() 
        }
        body = json.dumps(payload)
        
        on_request(self.mock_channel, mock_method, mock_properties, body)
        
        self.mock_channel.basic_publish.assert_not_called()
        
        self.mock_channel.basic_ack.assert_called_once_with(delivery_tag=mock_method.delivery_tag)
        
    @patch('pika.BlockingConnection')    
    def test_on_request_stale_request(self, mock_connection):
        mock_method = Mock()
        mock_properties = Mock()
        
        payload = {
            'user_email': 'mahit@shu.com',
            'meter_reading': 20,
            'timestamp': (datetime.now() - timedelta(seconds=20)).isoformat()
        }
        body = json.dumps(payload)
        
        on_request(self.mock_channel, mock_method, mock_properties, body)
        
        self.mock_channel.basic_publish.assert_not_called()
        
        self.mock_channel.basic_ack.assert_called_once_with(delivery_tag=mock_method.delivery_tag)
         
if __name__ == '__main__':
    unittest.main()