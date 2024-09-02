from playwright.sync_api import sync_playwright, Page
import os
import re
import calendar
from datetime import datetime, timedelta
import pandas as pd
import time
from fuzzywuzzy import fuzz
import json

start_date = '2024-08-01'
end_date = '2024-08-31'
chromium_path = os.getenv("CHROMIUM_PATH")
executable_file = 'chrome'
executable_path = os.path.join(chromium_path, executable_file)
headless_option = False
sort_option = 'recent'

product_name='Portable Electric Stove Single Burner 1000W Hot Plate JX1010B'
product_url='https://www.lazada.com.ph/portable-electric-stove-single-burner-1000w-hot-plate-jx1010b-i139390960-s157858946.html'

def to_navigate(page):
    retries = 2
    current_retry = 0
    initial_access=True
    while current_retry < retries:
        try:
            if initial_access is True:
                initial_access=False
                page.goto('https://www.lazada.com.ph', wait_until='load') 
                page.wait_for_load_state('load') 
                print('The page has fully loaded')
                current_retry += 3
            else: 
                page.wait_for_load_state('load')
                print('The page has fully loaded')
                current_retry += 3
        except Exception:
            print('Error occurred while navigating the page, captcha found')
            current_retry += 1

def get_matching_pattern(pattern_type):
    if pattern_type == 'selling_price':
        matching_pattern = r'(\d+[^a-zA-Z0-9]\d+|\d+)'
    elif pattern_type == 'total_ratings':
        matching_pattern = r'(\d+\.?\d*)'
    elif pattern_type == 'urls':
        matching_pattern = r'//(.*)'
    return matching_pattern        


def get_text_map():
    text_map = {
        'weeks': 7,
        'minutes': 1/1440,
        'minute': 1/1440,
        'week': 7,
        'hour': 1/24,
        'hours': 1/24,
        'days': 1,
        'day': 1
    }
    return text_map

def get_month_map():
    month_map = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
        'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
        'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    return month_map

def search_product(page, input_product):
    retries = 2
    current_retry = 0
    while current_retry < retries:
        try:
            page.wait_for_selector('div.search-box__bar--29h6')
            search_bar = page.query_selector('div.search-box__bar--29h6 input')
            if search_bar:
                search_bar.fill(input_product)
            page.keyboard.press("Enter")
            print(f'Product {input_product} has been searched')
            page.wait_for_load_state('load')
            current_retry += 3
        except Exception:
            print('Error occured while searching the products, captcha found')
            current_retry += 1

def click_product(page, product_url):
    retries = 2
    current_retry = 0
    try:
        page.wait_for_selector('div.ant-modal-content')
        over18_button = page.query_selector('div.ant-modal-content button.ant-btn.css-1bkhbmc.app.ant-btn-primary.uVxk9')
        if over18_button:
            over18_button.click()
            print('Clicked the "Over 18" button')
    except Exception:
        print('No over 18 button found')
    similarity_raito = 80
    while current_retry < retries:
        try:
            page.wait_for_selector('button.ant-pagination-item-link')
            trim_pattern = get_matching_pattern('urls')
            page.wait_for_selector('div._17mcb')
            all_products = page.query_selector('div._17mcb').query_selector_all('div.Bm3ON div._95X4G')
            for product in all_products:
                laz_product_url = product.query_selector('a').get_attribute('href')
                laz_clean_url = re.search(trim_pattern, laz_product_url).group(1)
                if fuzz.ratio(laz_clean_url, product_url) >= similarity_raito:
                    product.click()
                    page.wait_for_load_state('load')
                    print('The product has been clicked')
                    return
            next_button = page.query_selector_all('button.ant-pagination-item-link')[1]
            if next_button:
                next_button.click()
        except Exception:
            print('Error occured while click the product, capcha found')
            current_retry += 1
    return {
        'current_month': 0,
        'selling_price':0,
        'rating_value':0
    }

def get_total_ratings(page):
    retries = 2
    current_retry = 0
    while current_retry < retries:
        try:
            matching_pattern = get_matching_pattern('total_ratings')
            page.wait_for_load_state('load')
            rating_div = page.query_selector('div.pdp-review-summary a')
            if rating_div:
                rating_text = rating_div.text_content()
                re_found = re.search(matching_pattern, rating_text)
                if re_found:
                    return int(re_found.group(1))
                else:
                    return 0
            else:
                return 0
        except Exception:
            print('Error occured while getting the total ratings, capcha found')
            current_retry += 1
    return 0

def get_selling_price(page):
    retries = 2
    current_retry = 0
    while current_retry < retries:
        try:
            matching_pattern = get_matching_pattern('selling_price')
            page.wait_for_selector('div.pdp-product-price')
            price_element = page.query_selector('div.pdp-product-price span')
            if price_element:
                price_value = re.search(matching_pattern, price_element.text_content())
                if price_value:
                    try:
                        return int(price_value.group(1))
                    except Exception:
                        return float(price_value.group(1))
                else:
                    return 0
            else:
                return 0
        except Exception:
            print('Error while getting the selling price, capcha found')
            current_retry += 1
    return 0
    
def convert_to_datetime(date_string):
  try:
    return datetime.strptime(date_string, "%Y-%m-%d")
  except ValueError:
    return datetime.strptime(date_string, "%y-%m-%d")

  
def to_sort(page, sort_option):
    page.wait_for_timeout(3000)
    page_height = page.evaluate('() => window.innerHeight')
    total_height = page.evaluate('() => document.body.scrollHeight')
    middle_point = (page_height + total_height) / 3
    page.evaluate(f'window.scrollTo(0, {middle_point})')
    retries = 2
    current_retry = 0
    while current_retry < retries:
        try:
            page.wait_for_selector('div.oper', timeout=2000)
            sort_div = page.query_selector_all('div.oper')[1]
            if sort_div:
                sort_div.click()
            page.wait_for_selector('ul.next-menu-content')
            ul_element = page.query_selector('ul.next-menu-content')
            if ul_element:
                li_elements = ul_element.query_selector_all('li')
                for li in li_elements:
                    if li.text_content().lower() == sort_option:
                        li.click()
                        time.sleep(1)
                        return "Found"
        except Exception:
            print('Error occured while sorting the page, capcha found')
            current_retry += 1
    return "Not found"

def next_page(page):
    next_page_element = 'button.next-btn.next-btn-normal.next-btn-medium.next-pagination-item.next'
    page.wait_for_selector(next_page_element)
    next_button = page.query_selector(next_page_element)
    if next_button:
        next_button.click()

def check_continue(page, temp_list, start_date):
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    previous_month = start_date_obj - timedelta(days=1)
    previous_start_date = previous_month.replace(day=1)
    previous_end_date = previous_month.replace(day=calendar.monthrange(previous_month.year, previous_month.month)[1])
    try: 
        next_button_availability = page.query_selector('button.next-btn.next-btn-normal.next-btn-medium.next-pagination-item.next').get_attribute('disabled')
        if next_button_availability == '':
            return False
    except Exception as e:
        print(f'Find no next button to press, resolved error {e}')
        return False
    for datetime_obj in temp_list:
        if (datetime_obj.date() >= previous_start_date.date() and datetime_obj.date() <= previous_end_date.date()) or \
        (datetime_obj.date() < previous_start_date.date()):
            temp_list = []
            return False
    temp_list = []
    return True

def parse_day_pattern():
    day_pattern = r'(\d+)\s+\w+'
    year_pattern = r'\w+\s+(\d+)'
    month_pattern = r'\d+\s+(\w+)\s+\d+'
    ago_pattern = r'(\d+)\s+\w+\s+\w+'
    delay_pattern = r'\d+\s+(\w+)\s+\w+' 
    return day_pattern, month_pattern, year_pattern, ago_pattern, delay_pattern

def get_ratings(page):
    rating_count = 0
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') 
    day_pattern, month_pattern, year_pattern, ago_pattern, delay_pattern = parse_day_pattern()
    month_map = get_month_map()
    text_map = get_text_map()
    text_list = list(text_map.keys())
    total_pages = 60
    current_page = 0
    while current_page < total_pages:
        try:
            temp_list = []
            page.wait_for_selector('div.mod-reviews')
            ratings_div = page.query_selector('div.mod-reviews')
            if ratings_div:
                current_page += 1
                all_items = ratings_div.query_selector_all('div.item')
                for item in all_items:
                    to_use_text_map = False
                    date_string = item.query_selector('div.top span').text_content().lower()
                    for text in text_list:
                        if text in date_string:
                            to_use_text_map = True
                            break
                    if to_use_text_map is False:
                        day_string = re.search(day_pattern, date_string).group(1)
                        year_string = re.search(year_pattern, date_string).group(1)
                        month_string = month_map.get(re.search(month_pattern, date_string).group(1), "")
                        final_string = f'{year_string}-{month_string}-{day_string}'
                        datetime_obj = convert_to_datetime(final_string)
                        temp_list.append(datetime_obj)
                        if datetime_obj.date() >= start_date_obj.date() and datetime_obj.date() <= end_date_obj.date():
                            rating_count += 1
                    else:
                        current_date = datetime.now() - timedelta(days=1)
                        ago_value = int(re.search(ago_pattern, date_string).group(1))
                        delay_value = int(text_map.get(re.search(delay_pattern, date_string).group(1)))
                        delay_days = ago_value * delay_value
                        datetime_obj = current_date - timedelta(days=delay_days)
                        temp_list.append(datetime_obj)
                        if datetime_obj.date() >= start_date_obj.date() and datetime_obj.date() <= end_date_obj.date():
                            rating_count += 1
                to_continue = check_continue(page, temp_list, start_date)
        except Exception:
            print('Captcha found, fail getting the current ratings')
            return 0
        try: 
            if to_continue is True:
                next_page(page)
            else: 
                return rating_count
        except Exception:
            print('Captcha found, failed to capture the rating, capcha found')
            return 0
    return rating_count

def main(page):
    to_navigate(page)
    print(f'Connected to page {page}')
    search_product(page, product_name)
    final_map = click_product(page, product_url)
    if final_map:
        print('Fail getting the products')
        return final_map
    else:
        print("Start getting the SKUs'information")
        sort_decision = to_sort(page, sort_option)
        rating_value = get_total_ratings(page)
        selling_price = get_selling_price(page)
        if sort_decision == "Found":
            ratings = get_ratings(page)
        else:
            ratings = 0
        print(f'Total ratings: {rating_value}')
        print(f'Selling price: {selling_price}')
        print(f'Rating this month: {ratings}')
        final_map = {
            'current_month': ratings,
            'rating_value': rating_value,
            'selling_price':selling_price
            }
    return final_map

if __name__ == '__main__':
    with sync_playwright() as pw: 
            print('Start connecting to the browser')
            browser = pw.chromium.launch(executable_path=executable_path, headless=headless_option)
            context = browser.new_context(viewport={
                'height': 650,
                'width': 1300
            })
            page = context.new_page()
    main(page)
