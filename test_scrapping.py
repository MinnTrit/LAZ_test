import unittest
from playwright.sync_api import sync_playwright
from scrapping import (
    to_navigate,
    search_product,
    click_product,
    get_sku_informations
)
import threading
import os

class TestPlaywrightFunctions(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.chromium_path = os.getenv("CHROMIUM_PATH")
        self.executable_path = os.path.join(self.chromium_path, "chrome")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(executable_path=self.executable_path, headless=True)
        self.page = self.browser.new_page()

    @classmethod
    def tearDown(self):
        self.page.close()
        self.browser.close()
        self.playwright.stop()

    def test_search_product(self):
        input_product = 'Portable Electric Stove Single Burner 1000W Hot Plate JX1010B'
        product_url = 'https://www.lazada.com.ph/portable-electric-stove-single-burner-1000w-hot-plate-jx1010b-i139390960-s157858946.html'
        to_navigate(self.page)
        search_product(self.page, input_product)
        click_product(self.page, product_url)
        sort_option='recent'
        final_map = get_sku_informations(self.page, sort_option)
        self.assertIsInstance(final_map, dict)

if __name__ == '__main__':
    unittest.main()
