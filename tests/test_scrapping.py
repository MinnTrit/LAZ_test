import unittest
import re
from playwright.sync_api import sync_playwright
from src.scrapping import (
    convert_to_datetime,
    get_text_map,
    get_month_map,
    to_navigate,
    search_product,
    click_product,
    get_total_ratings,
    get_selling_price,
    to_sort,
    get_ratings,
    check_continue,
    parse_day_pattern
)
import os
from datetime import datetime
import random

class TestPlaywrightFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.start_date = '2024-08-01'
        cls.end_date = '2024-08-31'
        input_product = 'Portable Electric Stove Single Burner 1000W Hot Plate JX1010B'
        product_url = 'https://www.lazada.com.ph/portable-electric-stove-single-burner-1000w-hot-plate-jx1010b-i139390960-s157858946.html'
        cls.chromium_path = os.getenv("CHROMIUM_PATH")
        cls.executable_path = os.path.join(cls.chromium_path, "chrome")
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(executable_path=cls.executable_path, headless=True)
        cls.page = cls.browser.new_page()
        to_navigate(cls.page)
        search_product(cls.page, input_product)
        click_product(cls.page, product_url)

    @classmethod
    def tearDownClass(cls):
        cls.page.close()
        cls.browser.close()
        cls.playwright.stop()

    def test_get_month_map(self):
        month_map = get_month_map()
        self.assertIsInstance(month_map, dict)

    def test_get_text_map(self):
        text_map = get_text_map()
        self.assertIsInstance(text_map, dict)

    def test_false_check_continue(self, start_date, end_date):
        temp_list = ['2024-08-12', '2024-07-31']
        continue_decision = check_continue(self.page, temp_list, start_date, end_date)
        self.assertFalse(continue_decision)

    def test_true_check_continue(self, start_date, end_date):
        temp_list = ['2024-08-19', '2024-08-10']
        continue_decision = check_continue(self.page, temp_list, start_date, end_date)
        self.assertTrue(continue_decision)

    def test_parse_day_pattern(self):
        test_string = {
            'day': '10 Jun 2024',
            'year': '8 Jul 2025',
            'month': '5 Apr 2024',
            'ago': '3 days ago',
            'delay': '5 hours ago'
        }
        day_pattern, month_pattern, year_pattern, ago_pattern, delay_pattern = parse_day_pattern()
        
        #Write the test to match the day
        day_match = re.search(day_pattern, test_string['day'])
        self.assertIsNotNone(day_match.group(1), "Day pattern did not find")
        self.assertEqual(day_match.group(1), "10", "Day pattern did not match")

        #Write the test to match the month
        month_match = re.search(month_pattern, test_string['month'])
        self.assertIsNotNone(month_match.group(1), "Month pattern did not match")
        self.assertEqual(month_match.group(1), 'Apr', "Month pattern did not match")

        #Write the test to match the year
        year_match = re.search(year_pattern, test_string['year'])
        self.assertIsNotNone(year_match.group(1), "Year pattern did not match")
        self.assertEqual(year_match.group(1), "2025", "Year pattern did not match")

        #Write the test to test the ago time
        ago_match = re.search(ago_pattern, test_string['ago'])
        self.assertIsNotNone(ago_match.group(1), "Ago pattern did not match")
        self.assertEqual(ago_match.group(1), "3", "Ago pattern did not match")

        #Write the test to test the delay attribute
        delay_match = re.serach(delay_pattern, test_string['delay'])
        self.assertIsNotNone(delay_match.group(1), "Delay pattern did not match")
        self.assertEqual(delay_match.group(1), "hours", "Delay pattern did not match")

    def test_convert_to_datetime(self):
        first_test_string = '2024-07-08'
        second_test_string = '24-07-08'
        first_datetime = convert_to_datetime(first_test_string)
        second_datetime = convert_to_datetime(second_test_string)
        self.assertIsInstance(first_datetime, datetime)
        self.assertIsInstance(second_datetime, datetime)

    def test_to_sort(self):
        sort_option='recent'
        sort_decision = to_sort(self.page, sort_option)
        self.assertIsInstance(sort_decision, str)

    def test_get_total_ratings(self):
        rating_value = get_total_ratings(self.page)
        self.assertIsInstance(rating_value, int)
    
    def test_get_selling_price(self):
        selling_price = get_selling_price(self.page)
        self.assertIsInstance(selling_price, int)

    def test_get_ratings(self):
        ratings = get_ratings(self.page)
        self.assertIsInstance(ratings, int)

    def test_full_work_flow(self):
        rating_value = get_total_ratings(self.page)
        selling_price = get_selling_price(self.page)
        current_rating = get_ratings(self.page)
        final_map = {
            'rating_value': rating_value,
            'selling_price': selling_price,
            'current_rating': current_rating
        }
        self.assertIsInstance(final_map, dict)

if __name__ == '__main__':
    unittest.main()
