from playwright.sync_api import sync_playwright
import os
import re
import calendar
from datetime import datetime, timedelta
import pandas as pd
import time
from fuzzywuzzy import fuzz
import json

start_date = '2024-08-25'
end_date = '2024-08-31'
chromium_path = os.getenv("CHROMIUM_PATH")
executable_file = 'chrome.exe'
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
            print('Error occurred while navigating the page')
            current_retry += 1

def date_generator(start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    generated_dates = []
    current_date = start_date
    while current_date <= end_date:
        generated_dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    return generated_dates

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
            current_retry += 3
        except Exception:
            print('Error occured while searching the products')
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
            trim_pattern = r'//(.*)'
            page.wait_for_selector('div._17mcb')
            all_products = page.query_selector('div._17mcb').query_selector_all('div.Bm3ON div._95X4G')
            for product in all_products:
                laz_product_url = product.query_selector('a').get_attribute('href')
                laz_clean_url = re.search(trim_pattern, laz_product_url).group(1)
                if fuzz.ratio(laz_clean_url, product_url) >= similarity_raito:
                    product.click()
                    print('The product has been clicked')
                    return
            next_button = page.query_selector_all('button.ant-pagination-item-link')[1]
            if next_button:
                next_button.click()
        except Exception:
            print('Error occured while click the product')
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
            matching_pattern = r'(\d+\.?\d*)'
            page.wait_for_load_state('load')
            rating_div = page.query_selector('div.pdp-review-summary a')
            if rating_div:
                rating_text = rating_div.text_content()
                re_found = re.search(matching_pattern, rating_text)
                if re_found:
                    return re_found.group(1)
                else:
                    return 0
            else:
                return 0
        except Exception:
            print('Error occured while getting the total ratings')
            current_retry += 1
    return 0

def get_selling_price(page):
    error_string = "Not found"
    matching_pattern = r'(\d+[^a-zA-Z0-9]\d+)'
    page.wait_for_selector('div.pdp-product-price')
    price_text = page.query_selector('div.pdp-product-price span')
    if price_text:
        price_value = re.search(matching_pattern, price_text.text_content())
        if price_value:
            return price_value.group(1)
        else:
            return error_string
    else:
        return error_string
    
def convert_to_datetime(date_string):
  try:
    return datetime.strptime(date_string, "%Y-%m-%d")
  except ValueError:
    return datetime.strptime(date_string, "%y-%m-%d")
  
def check_sliding(page):
    try:
        page.wait_for_load_state('load')
        slide_bar = page.query_selector('div.bannar')
        if slide_bar:
            box = slide_bar.bounding_box()
            start_x = box['x']
            start_y = box['y'] + box['height'] / 2
            end_x = start_x + box['width']
            page.mouse.move(start_x, start_y)
            page.mouse.down()
            page.mouse.move(end_x, start_y, steps=100)
            page.mouse.up()
    except Exception as e:
        print(f"There's no sliding bar, error as {e}")
  
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
            print('Error occured while sorting the page')
            current_retry += 1
    return "Not found"

def next_page(page):
    page.wait_for_selector('button.next-btn.next-btn-normal.next-btn-medium.next-pagination-item.next')
    next_button = page.query_selector('button.next-btn.next-btn-normal.next-btn-medium.next-pagination-item.next')
    if next_button:
        next_button.click()

def check_continue(page, temp_list):
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
        if (datetime_obj >= previous_start_date and datetime_obj <= previous_end_date) or \
        (datetime_obj < previous_start_date):
            temp_list = []
            return False
    temp_list = []
    return True

def get_clean_string(customore_string):
    clean_url = customore_string.replace(re.search(r'.*(-s\d+).*', customore_string).group(1), "")
    return clean_url

def read_dataframe():
    current_directory = os.getcwd()
    file_name = 'scrapping_laz.xlsx'
    file_path = os.path.join(current_directory, file_name)
    df = pd.read_excel(file_path)
    df['clean_url'] = df['products_url'].apply(lambda row: get_clean_string(row))
    df.drop(columns=['products_url'], inplace=True)
    return df.values.tolist()

def get_ratings(page):
    rating_count = 0
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') 
    day_pattern = r'(\d+)\s+\w+'
    year_pattern = r'\w+\s+(\d+)'
    month_pattern = r'\d+\s+(\w+)\s+\d+'
    month_map = get_month_map()
    text_map = get_text_map()
    text_list = list(text_map.keys())
    total_pages = 60
    current_page = 0
    while current_page < total_pages:
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
                    ago_pattern = r'(\d+)\s+\w+\s+\w+'
                    delay_pattern = r'\d+\s+(\w+)\s+\w+'
                    ago_value = int(re.search(ago_pattern, date_string).group(1))
                    delay_value = int(text_map.get(re.search(delay_pattern, date_string).group(1)))
                    delay_days = ago_value * delay_value
                    datetime_obj = current_date - timedelta(days=delay_days)
                    temp_list.append(datetime_obj)
                    if datetime_obj.date() >= start_date_obj.date() and datetime_obj.date() <= end_date_obj.date():
                        rating_count += 1
            to_continue = check_continue(page, temp_list)
            try: 
                if to_continue is True:
                    next_page(page)
                    check_sliding(page)
                else: 
                    return rating_count
            except Exception:
                print('Captcha found, failed to capture the rating')
                return 0
    return rating_count

def get_sku_informations(page, sort_option):
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
    return {
        'current_month': ratings,
        'rating_value': rating_value,
        'selling_price':selling_price
        }

if __name__ == '__main__':
    with sync_playwright() as pw: 
        print('Start connecting to the browser')
        browser = pw.chromium.launch(executable_path=executable_path, headless=headless_option)
        context = browser.new_context(viewport={
            'height': 650,
            'width': 1300
        })
        page = context.new_page()
        to_navigate(page)
        print(f'Connected to page {page}')
        search_product(page, product_name)
        final_map = click_product(page, product_url)
        if final_map:
            print('Fail getting the products')
            df = pd.DataFrame(final_map, index='rating')
            df.to_clipboard(index=False, header=False)
        else:
            print("Start getting the SKUs'information")
            final_map = get_sku_informations(page, sort_option)
            #Push to the clipboard
            df = pd.DataFrame(final_map, index='rating')
            df.to_clipboard(index=False, header=False)
