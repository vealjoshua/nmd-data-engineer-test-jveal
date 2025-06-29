import pandas as pd
"Complete thes functions or write your own to perform the following tasks"

def calculate_profit_by_order(orders_df):
    "Calculate profit for each order in the DataFrame"
    
    orders_df['Profit'] = ((orders_df['List Price'] - orders_df['List Price'] * orders_df['Discount Percent']/100) - orders_df['cost price']) * orders_df['Quantity']

    return orders_df

def calculate_most_profitable_region(orders_df):
    "Calculate the most profitable region and its profit"
    
    region_profit = orders_df.groupby('Region')['Profit'].sum()
    most_profitable_region = region_profit.idxmax()
    max_profit = round(region_profit.max(), 2)

    result_df = pd.DataFrame({'Most Profitable Region': [most_profitable_region], 'Max Profit': [max_profit]})

    return result_df

def find_most_common_ship_method(orders_df):
    "Find the most common shipping method for each Category"
    
    shipping_method_counts = orders_df.groupby('Category')['Ship Mode'].value_counts()
    most_common_shipping_methods = shipping_method_counts.groupby(level=0).idxmax()
    result_df = most_common_shipping_methods.apply(lambda x: pd.Series([x[0], x[1]], index=['Category', 'Ship Mode']))
    return result_df

def find_number_of_order_per_category( orders_df):
    "find the number of orders for each Category and Sub Category"

    orders_by_category = orders_df.groupby(['Category', 'Sub Category'])['Quantity'].sum().reset_index()
    orders_by_category.columns = ['Category', 'Sub Category', 'Number of Orders']

    return orders_by_category
