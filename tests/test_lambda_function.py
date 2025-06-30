import os
import unittest
from unittest.mock import patch, MagicMock
import sys
import pandas as pd

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.lambda_function import get_s3_object_from_event, lambda_handler

class TestLambdaFunction(unittest.TestCase):
    def setUp(self):
        # Sample event data
        self.sample_event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'test-bucket'},
                    'object': {'key': 'test-file.csv'}
                }
            }]
        }
        
        # Sample DataFrame
        self.sample_df = pd.DataFrame({
            'Region': ['West', 'East', 'South'],
            'Profit': [100, 200, 150],
            'Category': ['Office Supplies', 'Furniture', 'Technology'],
            'Sub-Category': ['Binders', 'Chairs', 'Phones'],
            'Ship Mode': ['Standard Class', 'Second Class', 'First Class']
        })

    @patch('app.lambda_function.s3')
    def test_get_s3_object_from_event(self, mock_s3):
        """Test get_s3_object_from_event function"""
        # Mock S3 response with bytes-like data
        mock_response = {'Body': MagicMock()}
        mock_response['Body'].read.return_value = b'Some,CSV,Data\n1,2,3'
        mock_s3.get_object.return_value = mock_response
        
        response = get_s3_object_from_event(self.sample_event)
        
        mock_s3.get_object.assert_called_once_with(
            Bucket='test-bucket',
            Key='test-file.csv'
        )
        self.assertIsInstance(response, dict)

    @patch('app.lambda_function.s3')
    @patch('app.lambda_function.calculate_profit_by_order')
    @patch('app.lambda_function.calculate_most_profitable_region')
    @patch('app.lambda_function.find_most_common_ship_method')
    @patch('app.lambda_function.find_number_of_order_per_category')
    @patch('pandas.read_csv')
    @patch('pandas.DataFrame.to_csv')
    def test_lambda_handler(self, mock_to_csv, mock_read_csv, mock_find_number_of_order_per_category,
                          mock_find_most_common_ship_method, mock_calculate_most_profitable_region,
                          mock_calculate_profit_by_order, mock_s3):
        """Test lambda_handler function with valid data"""
        # Mock S3 response with bytes-like data
        mock_response = {'Body': MagicMock()}
        mock_response['Body'].read.return_value = b'Some,CSV,Data\n1,2,3'
        mock_s3.get_object.return_value = mock_response

        # Mock return values
        mock_read_csv.return_value = self.sample_df
        mock_calculate_most_profitable_region.return_value = pd.DataFrame({'Region': ['East'], 'Profit': [200]})
        mock_find_most_common_ship_method.return_value = pd.DataFrame({'Category': ['Office Supplies'], 'Ship Mode': ['Standard Class']})
        mock_find_number_of_order_per_category.return_value = pd.DataFrame({'Category': ['Office Supplies'], 'Count': [1]})
        
        # Call the handler
        lambda_handler(self.sample_event, None)
        
        # Verify calls
        mock_read_csv.assert_called_once()
        mock_calculate_profit_by_order.assert_called_once_with(self.sample_df)
        mock_calculate_most_profitable_region.assert_called_once_with(self.sample_df)
        mock_find_most_common_ship_method.assert_called_once_with(self.sample_df)
        mock_find_number_of_order_per_category.assert_called_once_with(self.sample_df)
        mock_to_csv.assert_called()
        
        # Verify S3 upload calls
        expected_upload_calls = [
            ('most_profitable_region.csv', 'output_s3', 'most_profitable_region.csv'),
            ('most_common_ship_method.csv', 'output_s3', 'most_common_ship_method.csv'),
            ('number_of_orders_per_category.csv', 'output_s3', 'number_of_orders_per_category.csv')
        ]
        
        actual_upload_calls = [args for name, args, kwargs in mock_s3.upload_file.mock_calls]
        self.assertEqual(len(actual_upload_calls), 3)
        for call in expected_upload_calls:
            self.assertIn(call, actual_upload_calls)

    @patch('app.lambda_function.s3')
    @patch('app.lambda_function.calculate_profit_by_order')
    @patch('app.lambda_function.calculate_most_profitable_region')
    @patch('app.lambda_function.find_most_common_ship_method')
    @patch('app.lambda_function.find_number_of_order_per_category')
    @patch('pandas.read_csv')
    @patch('pandas.DataFrame.to_csv')
    def test_lambda_handler_s3_error(self, mock_to_csv, mock_read_csv, mock_find_number_of_order_per_category,
                                    mock_find_most_common_ship_method, mock_calculate_most_profitable_region,
                                    mock_calculate_profit_by_order, mock_s3):
        """Test lambda_handler with S3 error"""
        # Mock S3 response to raise error
        mock_s3.get_object.side_effect = Exception('S3 Error')
        
        with self.assertRaises(Exception):
            lambda_handler(self.sample_event, None)
        
        # Verify no analytics functions were called
        mock_read_csv.assert_not_called()
        mock_calculate_profit_by_order.assert_not_called()
        mock_calculate_most_profitable_region.assert_not_called()
        mock_find_most_common_ship_method.assert_not_called()
        mock_find_number_of_order_per_category.assert_not_called()
        mock_to_csv.assert_not_called()

    @patch('app.lambda_function.s3')
    @patch('app.lambda_function.calculate_profit_by_order')
    @patch('app.lambda_function.calculate_most_profitable_region')
    @patch('app.lambda_function.find_most_common_ship_method')
    @patch('app.lambda_function.find_number_of_order_per_category')
    @patch('pandas.read_csv')
    @patch('pandas.DataFrame.to_csv')
    def test_lambda_handler_empty_file(self, mock_to_csv, mock_read_csv, mock_find_number_of_order_per_category,
                                     mock_find_most_common_ship_method, mock_calculate_most_profitable_region,
                                     mock_calculate_profit_by_order, mock_s3):
        """Test lambda_handler with empty file"""
        # Configure pandas.read_csv to raise EmptyDataError
        mock_read_csv.side_effect = pd.errors.EmptyDataError("No columns to parse from file")
        
        # Mock S3 response with empty data
        mock_response = {'Body': MagicMock()}
        mock_response['Body'].read.return_value = b''
        mock_s3.get_object.return_value = mock_response
        
        with self.assertRaises(ValueError) as context:
            lambda_handler(self.sample_event, None)
        self.assertEqual(str(context.exception), "Empty CSV file detected")
        
        # Verify no analytics functions were called
        mock_read_csv.assert_called_once()
        mock_calculate_profit_by_order.assert_not_called()
        mock_calculate_most_profitable_region.assert_not_called()
        mock_find_most_common_ship_method.assert_not_called()
        mock_find_number_of_order_per_category.assert_not_called()
        mock_to_csv.assert_not_called()
        mock_s3.upload_file.assert_not_called()

    @patch('app.lambda_function.s3')
    @patch('app.lambda_function.calculate_profit_by_order')
    @patch('app.lambda_function.calculate_most_profitable_region')
    @patch('app.lambda_function.find_most_common_ship_method')
    @patch('app.lambda_function.find_number_of_order_per_category')
    @patch('pandas.read_csv')
    @patch('pandas.DataFrame.to_csv')
    def test_lambda_handler_invalid_csv(self, mock_to_csv, mock_read_csv, mock_find_number_of_order_per_category,
                                      mock_find_most_common_ship_method, mock_calculate_most_profitable_region,
                                      mock_calculate_profit_by_order, mock_s3):
        """Test lambda_handler with invalid CSV data"""
        # Configure pandas.read_csv to raise ParserError
        mock_read_csv.side_effect = pd.errors.ParserError("Error tokenizing data")
        
        # Mock S3 response with invalid CSV data
        mock_response = {'Body': MagicMock()}
        mock_response['Body'].read.return_value = b'Invalid,Data\n1,2,3\n4,5\n6,7,8,9'
        mock_s3.get_object.return_value = mock_response
        
        with self.assertRaises(ValueError):
            lambda_handler(self.sample_event, None)
        
        # Verify no analytics functions were called
        mock_s3.upload_file.assert_not_called()

if __name__ == '__main__':
    unittest.main()
