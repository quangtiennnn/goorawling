## WEB SCRAPING: 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

## PACKAGES:
import re
from unidecode import unidecode
import time
import os
import csv 
import pandas as pd
import numpy as np
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import random
import json
import io
import requests 
from PIL import Image
#====================== CHROME DRIVER SETUP ======================
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
}
chrome_options = Options()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox') 
chrome_options.add_argument("--incognito")
# chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-application-cache")
chrome_options.add_argument("--disable-cache")
chrome_options.add_argument("--disk-cache-size=0")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
#====================== DATA COLLECTION ======================
def data_collection(elem):
    try:
        name = elem.find(class_='d4r55').text
    except:
        name = ''
    try:
        infos = elem.find(class_='RfnDt').text.split(" · ")
    except:
        infos = ''
    try:
        collected_date = elem.find(class_='rsqaWe').text
    except:
        collected_date = ''
    try:
        review = elem.find(class_='wiI7pd').text
    except:
        review = ''
    try:
        categorize = [each.text for each in elem.find_all(class_='RfDO5c')]
    except:
        categorize = ''
    try:
        review_rating = elem.find('span', class_='kvMYJc').get('aria-label')
    except:
        review_rating = ''
    # Extract image URLs
    images = []
    try:
        image_buttons = elem.find_all('button', class_='Tya61d')
        for button in image_buttons:
            style = button.get('style', '')
            match = re.search(r'url\((.*?)\)', style)
            if match:
                image_url = match.group(1).strip('"\'')
                images.append(image_url)
    except:
        images = []

    # Return the original data along with the new images column
    return [name, infos, collected_date, review, categorize, review_rating, images]


#====================== LANGUAGES ======================
def change_language_to_english(url):
    # Parse the URL into components
    parsed_url = urlparse(url)
    
    # Parse the query parameters into a dictionary
    query_params = parse_qs(parsed_url.query)
    
    # Change the 'hl' parameter to 'en'
    query_params['hl'] = 'en'
    
    # Reconstruct the query string
    new_query = urlencode(query_params, doseq=True)
    
    # Reconstruct the full URL with the updated query string
    new_url = urlunparse(parsed_url._replace(query=new_query))
    
    return new_url

def change_language_to_vietnamese(url):
    # Parse the URL into components
    parsed_url = urlparse(url)
    
    # Parse the query parameters into a dictionary
    query_params = parse_qs(parsed_url.query)
    
    # Change the 'hl' parameter to 'en'
    query_params['hl'] = 'vi'
    
    # Reconstruct the query string
    new_query = urlencode(query_params, doseq=True)
    
    # Reconstruct the full URL with the updated query string
    new_url = urlunparse(parsed_url._replace(query=new_query))
    
    return new_url

#====================== REVIEW CRAWLING ======================
def get_reviews(driver, number_of_reviews, file_path, constant=0.25, thresh_hold=2000):
    #====================== LIMIT THE REVIEW ===============================
    if number_of_reviews > thresh_hold:
        number_of_reviews = thresh_hold
    if number_of_reviews != 0:
        # Wait for the reviews to load before proceeding
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.jftiEf'))
        )
        
    #====================== SCROLL ===============================
    start_time = time.time()
    ele_key_down = driver.find_element(By.CSS_SELECTOR, ".m6QErb.DxyBCb.kA9KIf.dS8AEf")
    while True:
        for _ in range(5):  # Send PAGE_DOWN 10 times per loop
            ele_key_down.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.1)
        elapsed_time = time.time() - start_time
        if elapsed_time > float(constant) * float(number_of_reviews):
            break
    
    #====================== TAG "MORE" ===============================
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "button.w8nwRe.kyuRq")
        for button in buttons:
            button.click()
    except Exception:
        pass
    
    #====================== KEEP TAG ORIGINAL ============================
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "button.kyuRq.WOKzJe")
        for button in buttons:
            button.click()
    except Exception:
        pass

    #====================== SAVE REVIEW ===============================
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    elems = soup.find_all(class_='jftiEf')
    data = []
    for elem in elems:
        new_data = data_collection(elem)
        data.append(new_data)    

    #====================== COLLECTING DATA =================================
    header = ['name', 'infos', 'collected_date', 'review', 'categorize', 'review_rating']
    if len(file_path.split('/')) > 1:
        directory = '/'.join(file_path.split('/')[:-1])
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    try:
        with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(header)
            csv_writer.writerows(data)    
    except Exception as e:
        print(f"Failed to write reviews to {file_path}: {e}")
        
        
#====================== IMAGE CRAWLING ======================
def move_to_all_photos(driver):
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[26]/div[2]/div[2]/div[2]/div[1]/button').click()

def tag_click(driver,tag):
    driver.find_element(By.XPATH, f'//div[contains(@class, "Gpq6kf") and contains(@class, "NlVald") and text()="{tag}"]').click()

def get_images(driver, file_path):
    restaurant_id = file_path.split("/")[-1].replace(".csv", "")
    # Get all tag names except 'All', 'Latest', 'Video', etc.
    elems = driver.find_elements(By.CSS_SELECTOR, '.Gpq6kf.NlVald')
    exclude_tags = {'tất cả', 'mới nhất', 'all', 'latest', 'video'}
    tag_names = [elem.text for elem in elems if elem.text.strip().lower() not in exclude_tags and elem.text.strip()]
    
    tag_images = {}
    for tag in tag_names:
        try:
            tag_click(driver, tag)
            time.sleep(random.uniform(1, 2))  # Wait for images to load after clicking tag
            image_loaded = driver.find_elements(By.CSS_SELECTOR, '.Uf0tqf.loaded')
            urls = []
            for image in image_loaded:
                style = image.get_attribute('style')
                match = re.search(r'url\((.*?)\)', style)
                if match:
                    url = match.group(1).replace('&quot;', '').strip('"')
                    urls.append(url)
            tag_images[tag] = urls
        except Exception:
            tag_images[tag] = []
    
    # Prepare directory
    if len(file_path.split('/')) > 1:
        directory = '/'.join(file_path.split('/')[:-1])
        if not os.path.exists(directory):
            os.makedirs(directory)

    # Write to JSON: filename = restaurant_id.json
    json_path = os.path.join(directory, f"{restaurant_id}.json")
    try:
        with open(json_path, mode='w', encoding='utf-8-sig') as file:
            json.dump({'restaurant_id': restaurant_id, 'images': tag_images}, file, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to write JSON for {restaurant_id}: {e}")


def get_menu(driver, file_path):
    restaurant_id = file_path.split("/")[-1].replace(".csv", "")
    # Prepare directory: menu/restaurant_id/

    # Prepare directory: go into the parent directory and create menu/restaurant_id
    if len(file_path.split('/')) > 1:
        parent_dir = '/'.join(file_path.split('/')[:-1])
    else:
        parent_dir = '.'

    menu_dir = os.path.join(parent_dir, "menu", restaurant_id)
    if not os.path.exists(menu_dir):
        os.makedirs(menu_dir)
    if not os.path.exists(menu_dir):
        os.makedirs(menu_dir)
    try:
        tag_click(driver, "Thực đơn")
        time.sleep(random.uniform(1, 2))  # Wait for the menu to load

        # Find all elements with class 'K4UgGe'
        buttons = driver.find_elements(By.CSS_SELECTOR, '.K4UgGe')
        # Filter those whose aria-label starts with "Ảnh "
        image_buttons = [
            btn for btn in buttons
            if btn.get_attribute('aria-label') and btn.get_attribute('aria-label').startswith('Ảnh ')
        ]

        for idx, btn in enumerate(image_buttons):
            btn.click()
            time.sleep(4)  # Wait for the image to load
            png_bytes = driver.get_screenshot_as_png()
            image = Image.open(io.BytesIO(png_bytes))

            # Crop the right half
            width, height = image.size
            right_half = image.crop((width // 2, 0, width, height))
            right_half.save(os.path.join(menu_dir, f"menu_{idx+1}.png"))
    except Exception as e:
        pass


#====================== GET RESTAURANT LINK ======================
def get_name_address_list(df):
    """
    Extracts restaurant names and addresses from a DataFrame and returns them as a list of strings.
    """
    return [" ".join([str(row['name']), str(row['address_string'])]) for _, row in df.iterrows()]

def get_restaurant_link(driver,restaurant_string:str):
    """
    Searches for a restaurant on Google Maps and returns the link to the first result.
    """
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.fontBodyMedium.searchboxinput.xiQnY')))
    input_goo = driver.find_element(By.CSS_SELECTOR, '.fontBodyMedium.searchboxinput.xiQnY')
    find_button = driver.find_element(By.CSS_SELECTOR, '.mL3xi')
    time.sleep(1)
    input_goo.clear()
    input_goo.send_keys(restaurant_string)
    find_button.click()
    time.sleep(3)
    try: 
        get_first_restaurant = driver.find_element(By.CSS_SELECTOR, '.hfpxzc')
        restaurant_link =  get_first_restaurant.get_attribute('href')
    except NoSuchElementException:
        restaurant_link = driver.current_url
    time.sleep(2)
    return change_language_to_vietnamese(restaurant_link)

#====================== REVIEW CRAWLING ======================
def google_crawl(restaurant_id: str, link, proxy: str, folder_name: str = 'crawled_data', images: bool = False, reviews: bool = False):
    try:
        images_path = f'{str(folder_name)}/images/{str(restaurant_id)}.csv'
        # menu_path = f'{str(folder_name)}/menu/{str(restaurant_id)}.csv'
        reviews_path = f'{str(folder_name)}/reviews/{str(restaurant_id)}.csv'
        
        #====================== DRIVER SETTINGS =====================
        if images:
            driver = webdriver.Chrome(options=get_chrome_options(proxy))
            actions = ActionChains(driver)
            driver.get(link)
            time.sleep(random.uniform(3, 5))
            all_photos = driver.find_element(By.CSS_SELECTOR, '.aoRNLd.kn2E5e.NMjTrf')
            all_photos.click()
            time.sleep(random.uniform(2, 3))

            try:
                all_photos.click()
                return 0
            except Exception:
                get_images(driver, images_path)
            time.sleep(random.uniform(1, 3))
        
        if reviews:
            #====================== RELOAD & ADD  ========================
            driver = webdriver.Chrome(options=get_chrome_options(reviews=True))
            actions = ActionChains(driver)
            driver.get(link)
            driver.execute_script("document.body.style.zoom='25%'")
            time.sleep(random.uniform(5, 7))
            #=============================================================
            element = WebDriverWait(driver, 25).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]'))
            )
            element.click()
            tag_click(driver, 'Bài đánh giá')
            time.sleep(random.uniform(1, 2))
            driver.find_element(By.CSS_SELECTOR, ".HQzyZ").click()
            time.sleep(random.uniform(1, 2))
            actions.send_keys(Keys.DOWN).perform()
            time.sleep(random.uniform(0.5, 1))
            actions.send_keys(Keys.ENTER).perform()
            time.sleep(random.uniform(1, 2))
            #=============================================================
            try:
                number_of_reviews = int(driver.find_element(
                    By.XPATH, 
                    '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[2]/div/div[2]/div[3]'
                ).text.split()[0].replace('.', ''))
            except:
                number_of_reviews = 0
            time.sleep(2)
            time.sleep(random.uniform(3, 5))
            
            # Uncomment this line to actually get reviews
            get_reviews(driver, number_of_reviews, reviews_path)
            driver.close()
        else:
            driver.close()

    except Exception as e:
        try:
            if driver:
                driver.quit()
        except:
            pass

### ROTATING PROXIES
# This function fetches a list of proxies from a URL and returns the first working proxy.
# It uses the requests library to test each proxy by making a request to httpbin.org.
# If a proxy is working, it returns the proxy address; otherwise, it returns None.
def get_first_working_proxy_from_url():
    url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
    response = requests.get(url)
    
    if response.status_code == 200:
        proxies_list = response.text.strip().splitlines()
        random.shuffle(proxies_list)  # Shuffle the proxy list
        for proxy in proxies_list:
            proxy_dict = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
            try:
                test = requests.get("http://httpbin.org/ip", proxies=proxy_dict, timeout=5)
                if test.status_code == 200:
                    return proxy
            except Exception:
                continue
    return None

def get_chrome_options(proxy=None, reviews=False):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument("--incognito")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-cache")
    options.add_argument("--disk-cache-size=0")
    options.add_argument("--disable-extensions")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if proxy:
        options.add_argument(f'--proxy-server=http://{proxy}')
    if reviews:
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.cookies": 2,
            "profile.managed_default_content_settings.javascript": 1,
            "profile.managed_default_content_settings.plugins": 2,
            "profile.managed_default_content_settings.popups": 2,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.managed_default_content_settings.media_stream": 2,
        }
        options.add_experimental_option("prefs", prefs)
    return options