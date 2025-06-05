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
def get_reviews(driver,number_of_reviews,file_path,constant = 0.55,thresh_hold = 1000):
    #====================== LIMIT THE REVIEW ===============================
    if number_of_reviews > thresh_hold:
        number_of_reviews = thresh_hold
    
    #====================== SCROLL ===============================
    start_time = time.time()
    ele_key_down= driver.find_element(By.CSS_SELECTOR, ".m6QErb.DxyBCb.kA9KIf.dS8AEf")
    while True:
        ele_key_down.send_keys(Keys.DOWN)
        elapsed_time = time.time() - start_time
        if elapsed_time > float(constant)*float(number_of_reviews):
            break
    
    #====================== TAG "MORE" ===============================
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "button.w8nwRe.kyuRq")
        for button in buttons:
            button.click()
    except:
        pass
    
    #====================== KEEP TAG ORIGINAL ============================
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "button.kyuRq.WOKzJe")
        for button in buttons:
            button.click()
    except:
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
    header = ['name','infos','collected_date','review','categorize','review_rating']
    if len(file_path.split('/')) > 1:
        directory = '/'.join(file_path.split('/')[:-1])
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    try:
        with open(file_path, mode='w', newline='',encoding='utf-8-sig') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(header)
            csv_writer.writerows(data)    
    except:
        pass
        

#====================== IMAGE CRAWLING ======================
def move_to_all_photos(driver):
    driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[26]/div[2]/div[2]/div[2]/div[1]/button').click()

def tag_click(driver,tag):
    driver.find_element(By.XPATH, f'//div[contains(@class, "Gpq6kf") and contains(@class, "NlVald") and text()="{tag}"]').click()

def get_images(driver,file_path):
    restaurant_id = file_path.split("/")[-1].replace(".csv", "")
    # Get all tag names except 'All' and 'Latest' :)
    elems = driver.find_elements(By.CSS_SELECTOR, '.Gpq6kf.NlVald')
    exclude_tags = {'tất cả', 'mới nhất', 'all', 'latest', 'video'}
    tag_names = [elem.text for elem in elems if elem.text.strip().lower() not in exclude_tags and elem.text.strip()]
    
    tag_images = {}
    for tag in tag_names:
        try:
            tag_click(driver,tag)
            time.sleep(random.uniform(1,2))  # Wait for images to load after clicking tag
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

    # Write to CSV: columns = restaurant_id, images (as JSON)
    try:
        with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(['restaurant_id', 'images'])
            csv_writer.writerow([restaurant_id, tag_images])
    except:
        pass


#====================== REVIEW CRAWLING ======================
def google_crawl(restaurant_id: str, link, folder_name: str = 'sample'):
    images_path = f'{folder_name}/images/{restaurant_id}.csv'
    reviews_path = f'{folder_name}/reviews/{restaurant_id}.csv'
    #====================== driver SETTINGS =====================
    driver = webdriver.Chrome(options=chrome_options)
    actions = ActionChains(driver)
    driver.get(link)
    
    ## Click on the "All" button to show all photos
    actions = ActionChains(driver)
    all_button = driver.find_element(By.XPATH, '//button[contains(@class, "K4UgGe") and @aria-label="Tất cả"]')
    
    actions.move_to_element(all_button).perform() # Move to the button and click it!!!
    time.sleep(random.uniform(1, 2))
    all_button.click()
    time.sleep(random.uniform(1, 2))
    get_images(driver,images_path)

    #====================== RELOAD & ADD  ========================
    driver.get(link)
    time.sleep(random.uniform(3, 5))
    #=============================================================
    driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]').click()
    tag_click(driver,'Bài đánh giá')

    time.sleep(random.uniform(1, 2))
    driver.find_element(By.CSS_SELECTOR, ".HQzyZ").click()
    # driver.find_element(By.CSS_SELECTOR, ".DVeyrd").click()       
    time.sleep(random.uniform(1, 2))
    actions.send_keys(Keys.DOWN).perform()
    time.sleep(random.uniform(0.5, 1))
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(random.uniform(1, 2))
    #=============================================================
    number_of_reviews = int(driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[2]/div/div[2]/div[3]').text.split()[0].replace('.', ''))
    
    time.sleep(2)
    time.sleep(random.uniform(3, 5))
    get_reviews(driver,number_of_reviews,reviews_path)