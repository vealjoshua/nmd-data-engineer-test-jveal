import boto3
import csv
import io
from decimal import *

s3 = boto3.client('s3')

def handler(event, context):
    # Get the bucket and key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Get the object from S3
    response = s3.get_object(Bucket=bucket, Key=key)

    # Read the CSV file
    reader = csv.reader(io.TextIOWrapper(io.BytesIO(response['Body'].read())))

    # Initialize variables to track the most profitable region
    regions = {}
    shipping_methods_per_category = {}
    number_of_orders = {}
    
    # Iterate over the rows in the CSV file
    for row in reader:
        # Skip the header row
        if row[8] == 'Region':
            continue

        # Extract the variables from the row
        ship_mode, region, category, sub_category, cost_price, list_price, quantity, discount_percent = row[2], row[8], row[9], row[10], Decimal(row[12]), Decimal(row[13]), Decimal(row[14]), Decimal(row[15])

        # Calculate the profit
        profit = (list_price - (list_price * discount_percent/100) - cost_price) * quantity
        if (region in regions):
            regions[region] += profit
        else:
            regions[region] = profit

        # Store the shipping method and category in a dictionary
        if (category in shipping_methods_per_category):
            if (ship_mode in shipping_methods_per_category[category]):
                shipping_methods_per_category[category][ship_mode] += 1
            else:
                shipping_methods_per_category[category][ship_mode] = 1
        else:
            shipping_methods_per_category[category] = {}
            shipping_methods_per_category[category][ship_mode] = 1
        
        # Calculate the number of orders for each category and subcategory
        if (category in number_of_orders):
            number_of_orders[category] += 1
        else:
            number_of_orders[category] = 1 
        
        if (sub_category in number_of_orders):
            number_of_orders[sub_category] += 1
        else:
            number_of_orders[sub_category] = 1

    # Get an iterator for the dictionary's keys
    dict_iterator = iter(regions)
    # Get the first element from the iterator
    first_key = next(dict_iterator)
    # Assign the most profitable and the most profitable region to the first element
    max_profit = regions[first_key]
    most_profitable_region = first_key
    # Print the most profitable region
    for key, value in regions.items():
        if value > max_profit:
            max_profit = value
            most_profitable_region = key

    # Create a CSV file
    with open('most_profitable_region.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write a header row
        writer.writerow(['Region', 'Most Common Shipping Method'])

        # Write some data rows
        writer.writerow([most_profitable_region, max_profit])
    
    most_profitable_region = f'The most profitable region is {most_profitable_region} with a profit of ${max_profit:.2f}'
    print(most_profitable_region)

    # Create a CSV file
    with open('most_common_shipping_methods_per_category.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write a header row
        writer.writerow(['Category', 'Most Common Shipping Method'])

        # Write some data rows

        for category, shipping_methods in shipping_methods_per_category.items():
            most_common_shipping_method = max(shipping_methods, key=shipping_methods.get)
            # print(f'The most common shipping method for {category} is {most_common_shipping_method}')
            writer.writerow([category, most_common_shipping_method])

    print('most_common_shipping_method:', most_common_shipping_method)

    # Create a CSV file
    with open('number_of_orders.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write a header row
        writer.writerow(['Category', 'Orders'])

        # Write some data rows
        for category, orders in number_of_orders.items():
            writer.writerow([category, orders])

    # Upload CSVs to S3
    output_bucket = 'output_s3'
    s3.upload_file('most_profitable_region.csv', output_bucket, 'most_profitable_region.csv')
    s3.upload_file('most_common_shipping_methods_per_category.csv', output_bucket, 'most_common_shipping_methods_per_category.csv')
    s3.upload_file('number_of_orders.csv', output_bucket, 'number_of_orders.csv')
