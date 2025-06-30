import unittest
import pandas as pd
import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.orders_analytics import calculate_profit_by_order, calculate_most_profitable_region, find_most_common_ship_method, find_number_of_order_per_category

class TestOrdersAnalytics(unittest.TestCase):
    def setUp(self):
        # Create sample data for testing
        self.sample_data = {
            'Order ID': [1, 2, 3],
            'Region': ['West', 'East', 'South'],
            'Category': ['Office Supplies', 'Furniture', 'Technology'],
            'Sub Category': ['Binders', 'Chairs', 'Phones'],
            'Ship Mode': ['Standard Class', 'Second Class', 'First Class'],
            'List Price': [100, 200, 150],
            'Discount Percent': [10, 20, 15],
            'cost price': [70, 140, 100],
            'Quantity': [2, 3, 4]
        }
        self.sample_df = pd.DataFrame(self.sample_data)

    def test_calculate_profit_by_order(self):
        """Test calculate_profit_by_order function"""
        result_df = calculate_profit_by_order(self.sample_df)
        
        # Verify profit calculation
        expected_profit = ((self.sample_df['List Price'] - 
                          self.sample_df['List Price'] * self.sample_df['Discount Percent']/100) - 
                          self.sample_df['cost price']) * self.sample_df['Quantity']
        
        # Reset index to match the expected profit series
        expected_profit = expected_profit.reset_index(drop=True)
        
        # Verify the profit values match
        self.assertTrue(all(result_df['Profit'] == expected_profit))
        self.assertTrue('Profit' in result_df.columns)

    def test_calculate_most_profitable_region(self):
        """Test calculate_most_profitable_region function"""
        # Add profit column to sample data
        sample_df_with_profit = self.sample_df.copy()
        sample_df_with_profit['Profit'] = [60, 360, 420]
        
        result_df = calculate_most_profitable_region(sample_df_with_profit)
        
        # Verify result
        self.assertEqual(result_df.iloc[0]['Most Profitable Region'], 'South')
        self.assertEqual(result_df.iloc[0]['Max Profit'], 420)

    def test_find_most_common_ship_method(self):
        """Test find_most_common_ship_method function"""
        # Create sample data with multiple entries for common ship methods
        sample_data = {
            'Category': ['Office Supplies', 'Office Supplies', 'Furniture', 'Technology'],
            'Ship Mode': ['Standard Class', 'Standard Class', 'Second Class', 'First Class']
        }
        sample_df = pd.DataFrame(sample_data)
        
        result_df = find_most_common_ship_method(sample_df)
        
        # Verify the DataFrame structure
        self.assertEqual(len(result_df), 3)
        self.assertEqual(list(result_df.columns), ['Category', 'Ship Mode'])
        
        # Verify the values exist in the DataFrame
        self.assertTrue('Office Supplies' in result_df['Category'].values)
        self.assertTrue('Standard Class' in result_df['Ship Mode'].values)
        self.assertTrue('Furniture' in result_df['Category'].values)
        self.assertTrue('Second Class' in result_df['Ship Mode'].values)
        self.assertTrue('Technology' in result_df['Category'].values)
        self.assertTrue('First Class' in result_df['Ship Mode'].values)

    def test_find_number_of_order_per_category(self):
        """Test find_number_of_order_per_category function"""
        # Create sample data with multiple entries
        sample_data = {
            'Category': ['Office Supplies', 'Office Supplies', 'Furniture', 'Technology'],
            'Sub Category': ['Binders', 'Binders', 'Chairs', 'Phones'],
            'Quantity': [2, 3, 4, 5]
        }
        sample_df = pd.DataFrame(sample_data)
        
        result_df = find_number_of_order_per_category(sample_df)
        
        # Verify result
        self.assertEqual(len(result_df), 3)
        self.assertEqual(list(result_df.columns), ['Category', 'Sub Category', 'Number of Orders'])
        self.assertTrue('Furniture' in result_df['Category'].values)
        self.assertTrue('Chairs' in result_df['Sub Category'].values)
        self.assertTrue('Office Supplies' in result_df['Category'].values)
        self.assertTrue('Binders' in result_df['Sub Category'].values)
        self.assertTrue('Technology' in result_df['Category'].values)
        self.assertTrue('Phones' in result_df['Sub Category'].values)

    def test_calculate_profit_by_order_edge_cases(self):
        """Test edge cases for calculate_profit_by_order"""
        # Test case with zero quantity
        zero_quantity_df = pd.DataFrame({
            'List Price': [100],
            'Discount Percent': [10],
            'cost price': [70],
            'Quantity': [0]
        })
        result = calculate_profit_by_order(zero_quantity_df)
        self.assertEqual(result['Profit'][0], 0)

        # Test case with negative discount
        negative_discount_df = pd.DataFrame({
            'List Price': [100],
            'Discount Percent': [-10],
            'cost price': [70],
            'Quantity': [2]
        })
        result = calculate_profit_by_order(negative_discount_df)
        self.assertTrue(result['Profit'][0] > 0)

        # Test case with zero cost price
        zero_cost_df = pd.DataFrame({
            'List Price': [100],
            'Discount Percent': [10],
            'cost price': [0],
            'Quantity': [2]
        })
        result = calculate_profit_by_order(zero_cost_df)
        self.assertTrue(result['Profit'][0] > 0)

    def test_calculate_most_profitable_region_edge_cases(self):
        """Test edge cases for calculate_most_profitable_region"""
        # Test case with single region
        single_region_df = pd.DataFrame({
            'Region': ['West'],
            'Profit': [100]
        })
        result = calculate_most_profitable_region(single_region_df)
        self.assertEqual(result.iloc[0]['Most Profitable Region'], 'West')
        self.assertEqual(result.iloc[0]['Max Profit'], 100)

        # Test case with negative profits
        negative_profit_df = pd.DataFrame({
            'Region': ['West', 'East'],
            'Profit': [-100, -200]
        })
        result = calculate_most_profitable_region(negative_profit_df)
        self.assertEqual(result.iloc[0]['Most Profitable Region'], 'West')
        self.assertEqual(result.iloc[0]['Max Profit'], -100)

    def test_find_most_common_ship_method_edge_cases(self):
        """Test edge cases for find_most_common_ship_method"""
        # Test case with single category
        single_category_df = pd.DataFrame({
            'Category': ['Office Supplies'],
            'Ship Mode': ['Standard Class']
        })
        result = find_most_common_ship_method(single_category_df)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['Category'], 'Office Supplies')
        self.assertEqual(result.iloc[0]['Ship Mode'], 'Standard Class')

        # Test case with equal frequency ship modes
        equal_freq_df = pd.DataFrame({
            'Category': ['Office Supplies', 'Office Supplies', 'Office Supplies'],
            'Ship Mode': ['Standard Class', 'Second Class', 'First Class']
        })
        result = find_most_common_ship_method(equal_freq_df)
        self.assertEqual(len(result), 1)  # Should return first ship mode found

if __name__ == '__main__':
    unittest.main()
