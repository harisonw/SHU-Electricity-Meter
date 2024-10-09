import unittest
from unittest.mock import Mock

def calculate_meter_reading(customer_reading, price_per_unit, reading_log):
    customer_cost = {}

    #update the reading log with the current reading and calc cost
    for customer_id, current_reading in customer_reading.items():
        if customer_id not in reading_log:
            reading_log[customer_id] = [current_reading] 
            total_usage = current_reading  
        else:
            previous_reading = reading_log[customer_id][-1] 
            total_usage = current_reading - previous_reading  
            reading_log[customer_id].append(current_reading)  

        #stops charging customer if negative usage
        if total_usage > 0:
            customer_cost[customer_id] = total_usage * price_per_unit
        else:
            customer_cost[customer_id] = 0

    return customer_cost


class CalculateMeterReading(unittest.TestCase):
    
    #resuable method
    def setUp(self):
        self.mock_storage = Mock()
        self.reading_log = {}

    def test_reading_calculation(self):
        self.mock_storage.get_readings.return_value = {
            'customer1': 54.63,
            'customer2': 30.12,
            'customer3': 15.06
        }

        mock_price_per_unit = 0.22 #kwh

        result = calculate_meter_reading(self.mock_storage.get_readings(), mock_price_per_unit, self.reading_log)

        expected_result = {
            'customer1': 54.63 * 0.22,
            'customer2': 30.12 * 0.22,
            'customer3': 15.06 * 0.22
        }

        self.assertEqual(result, expected_result)

        self.assertEqual(self.reading_log,{
            'customer1': [54.63],
            'customer2': [30.12],
            'customer3': [15.06]
        })

    def test_reading_log_updating(self):

        #inital readings
        self.reading_log = {
            'customer1': [10.02],
            'customer2': [15.11]
        }

        #new readings
        self.mock_storage.get_readings.return_value = {
        'customer1': 25.74,
        'customer2': 30.0 
        }

        mock_price_per_unit = 0.22

        result = calculate_meter_reading(self.mock_storage.get_readings(), mock_price_per_unit, self.reading_log)

        expected_result = {
            'customer1': (25.74 - 10.02) * 0.22,
            'customer2': (30.0 - 15.11) * 0.22
        }

        self.assertEqual(result, expected_result)

        self.assertEqual(self.reading_log, {
            'customer1': [10.02, 25.74], 
            'customer2': [15.11, 30.0]
        })

    def test_new_customer_added(self):
        self.reading_log = {
            'customer1': [10.0]
        }

        #new customer added and reading
        self.mock_storage.get_readings.return_value ={
            'customer2': 20.0
        }

        mock_price_per_unit = 0.22

        result = calculate_meter_reading(self.mock_storage.get_readings(), mock_price_per_unit, self.reading_log)

        expected_result = {
            'customer2': 20 * 0.22
        }

        self.assertEqual(result, expected_result)
        self.assertEqual(self.reading_log,{
            'customer1': [10.0],
            'customer2': [20.0]
        })

    def test_no_change_reading(self):
        self.reading_log ={
            'customer1':[20]
        }

        self.mock_storage.get_readings.return_value ={
            'customer1': 20
        }

        mock_price_per_unit = 0.22

        result = calculate_meter_reading(self.mock_storage.get_readings(), mock_price_per_unit, self.reading_log)

        expected_result = {
            'customer1': 0
        }

        self.assertEqual(result, expected_result)

    #negative test
    def test_empty_readings(self):
        self.mock_storage.get_readings.return_value = {}
        
        mock_price_per_unit = 0.22

        result = calculate_meter_reading(self.mock_storage.get_readings(), mock_price_per_unit, self.reading_log)

        expected_result = {}

        self.assertEqual(result, expected_result)
        self.assertEqual(self.reading_log, {})

    #negative test
    def test_zero_price_per_unit(self):
        self.mock_storage.get_readings.return_value = {
            'customer1': 54.63,
            'customer2': 30.12,
            'customer3': 15.06
        }

        mock_price_per_unit = 0 #kwh

        result = calculate_meter_reading(self.mock_storage.get_readings(), mock_price_per_unit, self.reading_log)

        expected_result = {
            'customer1': 0,
            'customer2': 0,
            'customer3': 0
        }

        self.assertEqual(result, expected_result)

        self.assertEqual(self.reading_log, {
        'customer1': [54.63],
        'customer2': [30.12],
        'customer3': [15.06]
        })

    #negative test
    def test_negative_readings(self):
        self.mock_storage.get_readings.return_value = {
            'customer1': -34.41,
            'customer2': -74.0
        }

        mock_price_per_unit = 0.22

        result = calculate_meter_reading(self.mock_storage.get_readings(), mock_price_per_unit, self.reading_log)

        #negative reading should not havve a cost
        expected_result = {
            'customer1': 0,
            'customer2': 0
        }

        self.assertEqual(result, expected_result)

    #negative test
    def test_incorrect_readings(self):
        self.mock_storage.get_readings.return_value ={
            'customer1': 'invalid',
            'customer2': None
        }

        mock_price_per_unit = 0.22

        try:
            calculate_meter_reading(self.mock_storage.get_readings(), mock_price_per_unit, self.reading_log)
        except (ValueError, TypeError):
            return #if error then test passes
        
        self.fail("error was not raised")




# Run tests
if __name__ == '__main__':
    unittest.main()