import unittest, json , pika
from unittest.mock import patch, Mock
from client.client import SmartMeterClient
from datetime import datetime 
#run test with = python -m unittest tests/test_client.py
#python -m unittest discover -s tests

class TestClient(unittest.TestCase):
        """
        Unit tests for the SmartMeterClient class using Mock
        Covers connection to the server, meter reading generation,
        sending meter readings and updating meter readings
        """
        @patch('pika.BlockingConnection') #mock the pika.blockingconnection for all tests
        def setUp(self, mock_connection):
            """
            Setup test env with a mocked app and rabbitmq connection
            """
            self.app_mock = Mock()
            
            self.mock_connection = mock_connection
            self.mock_channel = Mock()
            self.mock_connection.return_value.channel.return_value = self.mock_channel

            self.client = SmartMeterClient(app=self.app_mock)

        def test_connection_to_server_success(self):
            """
            test connecting to the server
            """
            self.client.connect_to_server()
            
            #verify connection and channel created
            self.mock_connection.assert_called_once()
            self.mock_channel.basic_consume.assert_called_once()
            
        def test_generate_meter_reading(self):
            """
            test generation of the meter reading
            checks that the reading has the right data and timestamp
            """
            #test data
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
            """
            test the sending of the meter reading to the queue
            checks correct use of basic_publish method
            """
            mock_channel = self.mock_connection.return_value.channel.return_value
            self.client.channel = mock_channel
            
            reading_data = {
            "id": 1,
            "user_email": "mahit@shu.com",
            "meter_reading": 20.32,
            "timestamp": datetime.now().isoformat()
            }
            
            #send reading
            result = self.client.send_meter_reading(reading_data)
            
            #check to see if basic_publish was called once with correct arguements
            mock_channel.basic_publish.assert_called_once()
            args, kwargs = mock_channel.basic_publish.call_args
            self.assertEqual(kwargs['routing_key'], 'meter_reading_queue')
            self.assertEqual(kwargs['exchange'], '')
            self.assertEqual(json.loads(kwargs['body']), reading_data)
            
        def test_update_meter_reading(self):
            """
            checks the updated reading value
            rabbitmq message sending
            ui display update
            """
            self.client.reading = 10.0  #initial
            fixed_increase = 2.5
            
            #mock dependancies
            with patch.object(self.client, 'send_meter_reading', return_value="15.25") as mock_send_method, patch('random.uniform', return_value=fixed_increase):        
                self.client.update_meter_readings(self.app_mock)
            
                expected_reading = 10.0 + fixed_increase
                
                self.assertEqual(self.client.reading, expected_reading)
            
                mock_send_method.assert_called_once()
                sent_data = mock_send_method.call_args[0][0]
                self.assertEqual(sent_data["meter_reading"], expected_reading)
            
                self.app_mock.update_main_display.assert_called_once_with("£15.25", f"{self.client.reading:.2f} kWh")
        
        #Negative Tests
        @patch('pika.BlockingConnection', side_effect=pika.exceptions.AMQPConnectionError)
        def test_update_connection_status_timeout(self, mock_connection):
            """
            testing timeout trying to connect to server
            """
            self.client.timeout_reading = 10.0
            self.client.connect_to_server()
            self.app_mock.update_connection_status.assert_called_with("error")
            
        @patch('pika.BlockingConnection', side_effect=pika.exceptions.AMQPConnectionError)
        def test_update_connection_status_failure(self, mock_connection):
            """
            test when server connection fails
            """
            self.client.connect_to_server()
            self.app_mock.update_connection_status.assert_called_with("error")
            
        def test_send_meter_reading_invalid_data(self):
            """
            testing invalid data
            """
            data = {
                "id": 1,
                "user_email": "mahit@shu.com",
                #missing 'meter reading field
                "timestamp": datetime.now().isoformat()
            }
            
            result = self.client.send_meter_reading(data)
            
            self.assertEqual(result, "invalid_data")
            self.mock_channel.basic_publish.assert_not_called()
            
            
if __name__ == "__main__":
    unittest.main()