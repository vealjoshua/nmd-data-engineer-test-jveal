import sys
import json
import os
import boto3
s3 = boto3.client('s3')
import csv
import io
import pandas as pd
from app.orders_analytics import *
"""
Modify this lambda function to perform the following questions

1. Find the most profitable Region, and its profit
2. What shipping method is most common for each Category
3. Output a glue table containing the number of orders for each Category and Sub Category
"""


def get_s3_object_from_event(event : dict) -> str:
    "Returns the S3 path from the lambda event record"
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Get the object from S3
    response = s3.get_object(Bucket=bucket, Key=key)

    return response

def lambda_handler(event, context):
    "Lambda function to process S3 events and perform analytics on orders data"
    try:
        # Get the bucket and key from the event
        response = get_s3_object_from_event(event)

        # Read CSV with error handling
        try:
            df = pd.read_csv(io.BytesIO(response['Body'].read()))
        except pd.errors.EmptyDataError:
            raise ValueError("Empty CSV file detected")
        except pd.errors.ParserError:
            raise ValueError("Invalid CSV format detected")
        
        calculate_profit_by_order(df)

        most_profitable_region = calculate_most_profitable_region(df)
        most_common_ship_method = find_most_common_ship_method(df)
        number_of_orders_per_category = find_number_of_order_per_category(df)

        print(most_profitable_region)
        print(most_common_ship_method)
        print(number_of_orders_per_category)

        most_profitable_region.to_csv('most_profitable_region.csv', index=False)
        most_common_ship_method.to_csv('most_common_ship_method.csv', index=False)
        number_of_orders_per_category.to_csv('number_of_orders_per_category.csv', index=False)
        
        output_bucket = 'output_s3'
        s3.upload_file('most_profitable_region.csv', output_bucket, 'most_profitable_region.csv')
        s3.upload_file('most_common_ship_method.csv', output_bucket, 'most_common_ship_method.csv')
        s3.upload_file('number_of_orders_per_category.csv', output_bucket, 'number_of_orders_per_category.csv')
    except ValueError as e:
        print(f"Error: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise
