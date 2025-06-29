# test_lambda.py
import unittest
from unittest.mock import patch, MagicMock
import io
import csv

class TestLambdaHandler(unittest.TestCase):
    @patch("boto3.client")
    @patch("app.lambda_function.s3")
    def test_handler(self, mock_s3, mock_boto_client):
        # Mock the s3.get_object response
        # mock_s3.get_object.return_value = {'Body': MagicMock(read=lambda: b'col1,col2\nval1,val2')}
        with open('sample_orders.csv', 'r') as f:
            reader = csv.reader(f)
            rows = [row for row in reader]

        # Create a mock response with the CSV data
        csv_bytes = '\n'.join([','.join(row) for row in rows]).encode('utf-8')

        mock_body = MagicMock()
        mock_body.read.return_value = csv_bytes

        mock_s3.get_object.return_value = {"Body": mock_body}


        event = {
            "Records": [
                {
                    "s3": {
                        "bucket": {"name": "test-bucket"},
                        "object": {"key": "test.csv"}
                    }
                }
            ]
        }

        from app.lambda_function import lambda_handler
        lambda_handler(event, {})

        mock_s3.get_object.assert_called_once_with(Bucket='test-bucket', Key='test.csv')
        
        # Check that the function uploaded the files to S3
        mock_s3.upload_file.assert_has_calls([
            unittest.mock.call('most_profitable_region.csv', 'output_s3', 'most_profitable_region.csv'),
            unittest.mock.call('most_common_ship_method.csv', 'output_s3', 'most_common_ship_method.csv'),
            unittest.mock.call('number_of_orders_per_category.csv', 'output_s3', 'number_of_orders_per_category.csv')
        ])

if __name__ == '__main__':
    unittest.main()
