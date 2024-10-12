import unittest, json , pika
from unittest.mock import patch, Mock
from client.client import SmartMeterClient 
#run test with = python -m unittest tests/test_client.py
#python -m unittest discover -s tests


class TestClient(unittest.TestCase):
        
        @patch('pika.BlockingConnection') #mock the pika.blockingconnection for all tests
        def setUp(self, mock_connection):
            self.app_mock = Mock() 
            #start the client
            with patch.object(SmartMeterClient, 'connect_to_server', return_value=None):
                self.client = SmartMeterClient(self.app_mock)

            self.mock_connection = mock_connection

        def test_connection_to_server(self):
            #resetting the mock connection to stop it being called after connection
            self.app_mock.reset_mock()

            mock_channel = Mock()
            self.mock_connection.return_value.channel.return_value = mock_channel 

            self.client.connect_to_server()

            self.app_mock.update_connection_status.assert_called_once_with("connected")
            self.assertEqual(self.app_mock.update_connection_status.call_count, 1)

        @patch('pika.BlockingConnection', side_effect=pika.exceptions.AMQPConnectionError) #mock connection failu
        def test_connection_to_server_failure(self, mock_connection):
            #resetting the mock connection to stop it being called after connection
            self.app_mock.reset_mock()

            self.client.connect_to_server()
            self.app_mock.update_connection_status.assert_called_once_with("error")

        def test_gen_meter_reading(self):
            #gen a meter reading
            reading = self.client.generate_meter_reading()

            self.assertIn("id", reading)
            self.assertIn("user_email", reading)
            self.assertIn("meter_reading", reading)
            self.assertIn("timestamp", reading)
            self.assertEqual(reading["user_email"], self.client.user_email)

if __name__ == "__main__":
    unittest.main()
