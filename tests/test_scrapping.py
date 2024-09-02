import unittest
from unittest.mock import MagicMock, patch
import re
from playwright.sync_api import sync_playwright
from src.scrapping import (
    convert_to_datetime,
    get_text_map,
    get_month_map,
    search_product,
    to_navigate,
    click_product,
    get_total_ratings,
    get_selling_price,
    to_sort,
    get_ratings,
    check_continue,
    parse_day_pattern,
    next_page
)
import os
from datetime import datetime
import random

class TestPlaywrightFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.start_date = '2024-08-01'
        cls.end_date = '2024-08-31'
        cls.product_name = 'Portable Electric Stove Single Burner 1000W Hot Plate JX1010B'
        cls.product_url = 'https://www.lazada.com.ph/portable-electric-stove-single-burner-1000w-hot-plate-jx1010b-i139390960-s157858946.html'
        cls.chromium_path = os.getenv("CHROMIUM_PATH")
        cls.executable_path = os.path.join(cls.chromium_path, "chrome")
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(executable_path=cls.executable_path, headless=True)
        cls.page = cls.browser.new_page()
        to_navigate(cls.page)

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

    def test_search_and_click_product(self):
        search_product(self.page, self.product_name)
        self.page.wait_for_selector('span.breadcrumb_item_anchor.breadcrumb_item_anchor_last')
        search_string = self.page.query_selector('span.breadcrumb_item_anchor.breadcrumb_item_anchor_last').text_content()
        self.assertEqual(search_string, 'Search Results')
        click_product(self.page, self.product_url)
        self.page.wait_for_selector('div.pdp-mod-product-badge-wrapper')
        product_string = self.page.query_selector('div.pdp-mod-product-badge-wrapper').text_content()
        self.assertEqual(product_string, self.product_name)

    @patch('src.scrapping.Page')
    def test_check_continue(self, MockPage):
        #Initialize the mock objects
        mock_page = MockPage.return_value
        mock_page.query_selector.get_attribute.return_value = 'Enable'
        temp_list = [datetime(2024, 7, 10), datetime(2024, 8, 17)]
        continue_decision = check_continue(mock_page, temp_list, self.start_date, self.end_date)
        self.assertFalse(continue_decision)
        mock_page.query_selector.assert_called_once()

    @patch('src.scrapping.Page')
    def test_true_check_continue(self, MockPage):
        #Initialize the mock objects
        mock_page = MockPage.return_value
        mock_button = MagicMock()
        mock_button.get_attribute.return_value = 'Enable'
        temp_list = [datetime(2024, 8, 22), datetime(2024, 8, 19)]
        continue_decision = check_continue(mock_page, temp_list, self.start_date, self.end_date)
        self.assertTrue(continue_decision)
        mock_page.query_selector.assert_called_once()

    @patch('src.scrapping.Page')
    def test_disable_check_continue(self, MockPage):
        #Initialize the mock objects
        mock_button = MagicMock()
        mock_page = MockPage.return_value
        mock_page.query_selector.return_value = mock_button
        mock_button.get_attribute.return_value = ''
        temp_list = [datetime(2024, 8, 22), datetime(2024, 8, 19)]
        continue_decision = check_continue(mock_page, temp_list, self.start_date, self.end_date)
        self.assertFalse(continue_decision)
        mock_page.query_selector.assert_called_once()
        mock_button.get_attribute.assert_called_once_with('disabled')

    def test_parse_day_pattern(self):
        test_string = {
            'day': '10 Jun 2024',
            'year': '8 Jul 2025',
            'month': '5 Apr 2024',
            'ago': '3 days ago',
            'delay': '5 hours ago'
        }
        day_pattern, month_pattern, year_pattern, ago_pattern, delay_pattern = parse_day_pattern()
        
        day_match = re.search(day_pattern, test_string['day'])
        self.assertIsNotNone(day_match.group(1), "Day pattern did not find")
        self.assertEqual(day_match.group(1), "10", "Day pattern did not match")

        month_match = re.search(month_pattern, test_string['month'])
        self.assertIsNotNone(month_match.group(1), "Month pattern did not match")
        self.assertEqual(month_match.group(1), 'Apr', "Month pattern did not match")

        year_match = re.search(year_pattern, test_string['year'])
        self.assertIsNotNone(year_match.group(1), "Year pattern did not match")
        self.assertEqual(year_match.group(1), "2025", "Year pattern did not match")

        ago_match = re.search(ago_pattern, test_string['ago'])
        self.assertIsNotNone(ago_match.group(1), "Ago pattern did not match")
        self.assertEqual(ago_match.group(1), "3", "Ago pattern did not match")

        delay_match = re.search(delay_pattern, test_string['delay'])
        self.assertIsNotNone(delay_match.group(1), "Delay pattern did not match")
        self.assertEqual(delay_match.group(1), "hours", "Delay pattern did not match")

    def test_convert_to_datetime(self):
        first_test_string = '2024-07-08'
        second_test_string = '24-07-08'
        first_datetime = convert_to_datetime(first_test_string)
        second_datetime = convert_to_datetime(second_test_string)
        self.assertIsInstance(first_datetime, datetime)
        self.assertIsInstance(second_datetime, datetime)

    @patch('src.scrapping.Page')
    def test_to_sort(self, MockPage):
        #Initialize the mock objects
        mock_page = MockPage.return_value
        mock_sort_div = MagicMock()
        mock_ul_element = MagicMock()
        mock_li_elements = [MagicMock() for _ in range(4)]

        #Configure the mock behaviors
        mock_sort_div.click = MagicMock()
        mock_ul_element.query_selector_all.return_value = mock_li_elements

        #Create the mock page
        mock_page = MagicMock()
        mock_page.wait_for_selector.return_value = None
        mock_page.wait_for_timeout.return_value = None
        mock_page.evaluate.side_effect = [1000, 3000, 0]
        mock_page.query_selector.return_value = mock_ul_element
        mock_page.query_selector_all.side_effect = [
            [MagicMock(), mock_sort_div],
            [mock_li_elements]
        ]
        #Trigger the mock objects
        mock_li_elements[0].text_content.return_value = 'Relevance'
        mock_li_elements[1].text_content.return_value = 'Recent'
        mock_li_elements[2].text_content.return_value = 'Rating: High to Low'
        mock_li_elements[3].text_content.return_value = 'Rating: Low to High'
        
        for li in mock_li_elements:
            li.click = MagicMock()

        sort_option='recent'
        sort_decision = to_sort(mock_page, sort_option)
        self.assertIsInstance(sort_decision, str)
        self.assertEqual(sort_decision, "Found")
        mock_page.wait_for_selector.assert_called()
        mock_page.evaluate.assert_called()
        mock_page.query_selector_all.assert_called()
        mock_sort_div.click.assert_called_once()
        mock_page.wait_for_selector.assert_called()
        mock_page.query_selector.assert_called()
        mock_ul_element.query_selector_all.assert_called()
        mock_li_elements[1].click.assert_called_once()

    @patch('src.scrapping.Page')
    def test_get_total_ratings(self, MockPage):
        mock_page = MockPage.return_value
        mock_page.wait_for_load_state.return_value = None
        rating_div = MagicMock()
        mock_page.query_selector.return_value = rating_div
        rating_div.text_content.return_value = '8347 Ratings'
        rating_value = get_total_ratings(mock_page)
        self.assertIsInstance(rating_value, int)
        mock_page.wait_for_load_state.assert_called()
        mock_page.query_selector.assert_called_once()
        rating_div.text_content.assert_called_once()
    
    @patch('src.scrapping.Page')
    def test_get_selling_price(self, MockPage):
        #Initialize the mock objects
        mock_page = MockPage.return_value
        mock_page.wait_for_selector.return_value = None
        mock_price_element = MagicMock()
        mock_page.query_selector.return_value = mock_price_element
        mock_price_element.text_content.return_value = '₱166.46'

        selling_price = get_selling_price(mock_page)
        self.assertIsInstance(selling_price, float)
        self.assertEqual(selling_price, 166.46)
        mock_page.wait_for_selector.assert_called_once()
        mock_page.query_selector.assert_called_once()
        mock_price_element.text_content.assert_called_once()

    @patch('src.scrapping.Page')
    def test_get_ratings(self, MockPage):
        mock_page = MockPage.return_value
        mock_page.wait_for_selector.return_value = None
        #Create the rating div
        mock_rating_div = MagicMock()
        mock_page.query_selector.return_value = mock_rating_div
        mock_items_div = [MagicMock() for _ in range(10)]
        mock_rating_div.query_selector_all.return_value = mock_items_div
        for item in mock_items_div:
            random_day = random.randint(1,28)
            random_month = random.randint(1, 12)
            datetime_obj = datetime(2024, random_month, random_day)
            date_string = datetime_obj.strftime('%d %b %Y').lower()
            item.query_selector.return_value.text_content.return_value = date_string

        ratings = get_ratings(mock_page)
        self.assertIsInstance(ratings, int)
        mock_page.query_selector.assert_called()
        mock_rating_div.query_selector_all.assert_called_once_with('div.item')
        for item in mock_items_div:
            item.query_selector.return_value.text_content.assert_called()
    
    @patch('src.scrapping.Page')
    def test_next_page(self, MockPage):
        mock_page = MockPage.return_value
        mock_page.wait_for_selector.return_value = None
        mock_button = MagicMock()
        mock_page.query_selector.return_value = mock_button
        mock_button.click.return_value = None

        next_page(mock_page)
        next_page_element = 'button.next-btn.next-btn-normal.next-btn-medium.next-pagination-item.next'
        mock_page.wait_for_selector.assert_called_once_with(next_page_element)
        mock_page.query_selector.assert_called_once_with(next_page_element)
        mock_button.click.assert_called_once()

if __name__ == '__main__':
    unittest.main()
