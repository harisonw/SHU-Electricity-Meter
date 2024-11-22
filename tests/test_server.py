import unittest, json , pika
from unittest.mock import patch, Mock
#from server.server import calculate_bill, meter_request
#run test with = python -m unittest tests/test_server.py
#python -m unittest discover -s tests

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

    @patch('pika.BlockingConnection')  #mock the pika.blockingconnection

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

        #checks
        self.mock_channel.basic_publish.assert_called_once_with(
            exchange='',
            routing_key='reply_queue',
            properties=pika.BasicProperties(correlation_id='test123'),
            body=json.dumps(float(expected_bill))
        )

        self.mock_channel.basic_ack.assert_called_once_with(delivery_tag=mock_method.delivery_tag)

    def test_negative_meter_readings(self):
        #mock method, properties, create a payload
        mock_method = Mock()
        mock_properties = Mock()
        mock_properties.reply_to = 'reply_queue'
        mock_properties.correlation_id = 'test123'

        payload = {
            'user_email': 'mahit@test.com',
            'meter_reading': -30,
            'timestamp': '2024-10-11T12:00:00Z'
        }
        body = json.dumps(payload)

        #raise an error for negative value
        with self.assertRaises(ValueError):
            meter_request(self.mock_channel, mock_method, mock_properties, body)

    def test_zero_meter_reading(self):
        #mock method, properties, create a payload
        mock_method = Mock()
        mock_properties = Mock()
        mock_properties.reply_to = 'reply_queue'
        mock_properties.correlation_id = 'test123'

        payload = {
            'user_email': 'mahit@test.com',
            'meter_reading': 0,
            'timestamp': '2024-10-11T12:00:00Z'
        }
        body = json.dumps(payload)

        meter_request(self.mock_channel, mock_method, mock_properties, body)

        #bill should be 0
        expected_bill = calculate_bill(0)

        self.mock_channel.basic_publish.assert_called_once_with(
            exchange='',
            routing_key='reply_queue',
            properties=pika.BasicProperties(correlation_id='test123'),
            body=json.dumps(float(expected_bill))
        )

    def test_invalid_json(self):
        #mock method, properties, create a payload
        mock_method = Mock()
        mock_properties = Mock()
        mock_properties.reply_to = 'reply_queue'
        mock_properties.correlation_id = 'test123'

        invalid_body = "this is not a json string"

        with self.assertRaises(json.JSONDecodeError):
            meter_request(self.mock_channel, mock_method, mock_properties, invalid_body)

    def test_missing_meter_reading(self):
        #mock method, properties, create a payload
        mock_method = Mock()
        mock_properties = Mock()
        mock_properties.reply_to = 'reply_queue'
        mock_properties.correlation_id = 'test123'

        payload = {
            'user_email': 'mahit@test.com',
            'timestamp': '2024-10-11T12:00:00Z'
         }
        body = json.dumps(payload)

        with self.assertRaises(KeyError):
            meter_request(self.mock_channel, mock_method, mock_properties, body)

    def test_missing_email(self):
        #mock method, properties, create a payload
        mock_method = Mock()
        mock_properties = Mock()
        mock_properties.reply_to = 'reply_queue'
        mock_properties.correlation_id = 'test123'

        payload = {
            'meter_reading': 32.5,
            'timestamp': '2024-10-11T12:00:00Z'
        }
        body = json.dumps(payload)

        with self.assertRaises(KeyError):
            meter_request(self.mock_channel, mock_method, mock_properties, body)
            
if __name__ == '__main__':
    unittest.main()
