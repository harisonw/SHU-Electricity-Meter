import unittest, json , pika
from unittest.mock import patch, Mock
from client.client import SmartMeterClient
from datetime import datetime 
#run test with = python -m unittest tests/test_client.py
#python -m unittest discover -s tests

#TODO: negative tests (timeouts) and comments and update meter reading

class TestClient(unittest.TestCase):
        
        @patch('pika.BlockingConnection') #mock the pika.blockingconnection for all tests
        def setUp(self, mock_connection):
            self.app_mock = Mock()
            self.mock_connection = mock_connection
            self.mock_channel = Mock()
            self.mock_connection.return_value.channel.return_value = self.mock_channel

            # Initialize the client with the mock app
            self.client = SmartMeterClient(app=self.app_mock)

        def test_connection_to_server_success(self):
            self.client.connect_to_server()
            
            #verify connection and channel created
            self.mock_connection.assert_called_once()
            self.mock_channel.basic_consume.assert_called_once()
            
        def test_generate_meter_reading(self):
            reading_id = 1
            reading = 23.5
            result = self.client.generate_meter_reading(reading_id, reading)
        
            expected_result = {
                "id": reading_id,
                "user_email": "shu@example.com",
                "meter_reading": reading,
                "timestamp": datetime.now().isoformat()
            }
        
            #check if result matches expected
            self.assertEqual(result["id"], expected_result["id"])
            self.assertEqual(result["user_email"], expected_result["user_email"])
            self.assertEqual(result["meter_reading"], expected_result["meter_reading"])
            self.assertTrue(result["timestamp"].startswith(str(datetime.now().year)))
            
        def test_send_meter_reading(self):
            mock_channel = self.mock_connection.return_value.channel.return_value
            self.client.channel = mock_channel
            
            reading_data = {
            "id": 1,
            "user_email": "mahit@shu.com",
            "meter_reading": 20.32,
            "timestamp": datetime.now().isoformat()
            }
            
            #call mehtod
            result = self.client.send_meter_reading(reading_data)
            
            mock_channel.basic_publish.assert_called_once()
            args, kwargs = mock_channel.basic_publish.call_args
            self.assertEqual(kwargs['routing_key'], 'meter_reading_queue')
            self.assertEqual(kwargs['exchange'], '')
            self.assertEqual(json.loads(kwargs['body']), reading_data)
            
        #def test_update_meter_reading(self):
            self.client.reading = 10.0  #initial
            MIN_INCREASE = 1.0
            MAX_INCREASE = 5.0
            
if __name__ == "__main__":
    unittest.main()