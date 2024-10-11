import unittest, json , pika
from unittest.mock import patch, Mock
from server.server_4 import calculate_bill, meter_request

class TestServer(unittest.TestCase):
    
    #resuable method
    def setUp(self):
        self.mock_connection = Mock()
        self.mock_channel = Mock()
        self.mock_connection.return_value.channel.return_value = self.mock_channel

    def test_calculate_bill(self):
        meter_reading = 100
        expected_bill = meter_reading * 0.15
        self.assertEqual(calculate_bill(meter_reading), expected_bill)

    @patch('pika.BlockingConnection')  #mock the pika.BlockingConnection

    def test_meter_request(self, mock_connection):
        #mock method, properties, create a payload
        mock_method = Mock()
        mock_properties = Mock()
        mock_properties.reply_to = 'reply_queue'
        mock_properties.correlation_id = 'test123'

        payload = {
            'user_email': 'mahit@test.com',
            'meter_reading': 32.5,
            'timestamp': '2024-10-11T12:00:00Z'
        }
        body = json.dumps(payload)

        #call function
        meter_request(self.mock_channel, mock_method, mock_properties, body)

        # Expected bill calculation
        expected_bill = calculate_bill(32.5)

        #debug
        print(f"Expected bill: {expected_bill}")
        #print(f"mock_publish calls: {self.mock_channel.basic_publish.call_args_list}")

        #checks
        self.mock_channel.basic_publish.assert_called_once_with(
            exchange='',
            routing_key='reply_queue',
            properties=pika.BasicProperties(correlation_id='test123'),
            body=json.dumps(float(expected_bill))
        )

        self.mock_channel.basic_ack.assert_called_once_with(delivery_tag=mock_method.delivery_tag)

if __name__ == '__main__':
    unittest.main()
