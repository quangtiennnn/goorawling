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


#====================== CHROME DRIVER SETUP ======================
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
}
chrome_options = Options()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox') 
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-application-cache")
chrome_options.add_argument("--disable-cache")
chrome_options.add_argument("--disk-cache-size=0")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])


#====================== LINK CRAWLING ======================
def googlemapCrawl(district, city = 'Thành phố Hồ Chí Minh'):
    kw_input = f"Nhà hàng ở {district}, {city}"
    #====================== SEARCH ====================================
    browser = webdriver.Chrome(options=chrome_options)
    path_search = "https://www.google.com/maps?hl=vi-VN"
    browser.get(path_search)
    input_search = browser.find_element(By.ID, "searchboxinput")
    input_search.send_keys(kw_input)
    input_search.send_keys(Keys.ENTER)
    sleep(5)
    #====================== SCROLL DOWN ===============================
    start_time = time.time()
    
    scroll_items = browser.find_elements(By.CLASS_NAME, "hfpxzc")
    while True:
      try:
        element = browser.find_element(By.CSS_SELECTOR, 'span.HlvSq')
        break
      except NoSuchElementException:
        scroll_items[1].send_keys(Keys.DOWN)
        # Timeout handling
        elapsed_time = time.time() - start_time
        if elapsed_time > 300:
            print("Timeout exceeded. Exiting loop.")
            break
    #====================== HTML CONTENTS ===============================
    html_content = browser.page_source
    browser.quit()
    soup = BeautifulSoup(html_content, 'html.parser')
    elements = soup.find_all(class_='hfpxzc')
    
    if not os.path.exists('data_crawl_link'):
          os.makedirs(directory_name)
    filename = f'data_crawl_link/{unidecode(str(district).lower())}_{unidecode(city.lower())}.txt'
    with open(filename, 'w', encoding='utf-8') as output_file:
        # Extract and write the href attributes to the file
        for element in elements:
            href = element.get('href')
            if href:
                output_file.write(href + '\n')
    output = f"Saved to {filename}"
    print(output)


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


#====================== REVIEW CRAWLING ======================
def getReviews(browser,number_of_reviews,file_path,constant = 0.55,thresh_hold = 1000):
    
    #====================== LIMIT THE REVIEW ===============================
    if number_of_reviews > 1000:
        number_of_reviews = thresh_hold
    
    #====================== SCROLL ===============================
    start_time = time.time()
    ele_key_down= browser.find_element(By.CSS_SELECTOR, ".m6QErb.DxyBCb.kA9KIf.dS8AEf")
    while True:
        ele_key_down.send_keys(Keys.DOWN)
        elapsed_time = time.time() - start_time
        if elapsed_time > float(constant)*float(number_of_reviews):
            break
    
    #====================== TAG "MORE" ===============================
    try:
        buttons = browser.find_elements(By.CSS_SELECTOR, "button.w8nwRe.kyuRq")
        for button in buttons:
            button.click()
    except:
        pass
    
    #====================== KEEP TAG ORIGINAL ============================
    try:
        buttons = browser.find_elements(By.CSS_SELECTOR, "button.kyuRq.WOKzJe")
        for button in buttons:
            button.click()
    except:
        pass

    #====================== SAVE REVIEW ===============================
    html_content = browser.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    elems = soup.find_all(class_='jftiEf')
    data = []
    for elem in elems:
        new_data = data_collection(elem)
        data.append(new_data)

        # Print progress
        print(f"{file_path} {i}/{number_of_reviews}")
    
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
        
def reviewCrawl(link,folder_name = 'sample'):
    #====================== NAME =================================
    coordinates = link.split('/')[6].split("=")[1].split("!")[5:7]
    name = f"{coordinates[0][2:]},{coordinates[1][2:]}"
    #====================== BROWSER SETTINGS =====================
    browser = webdriver.Chrome(options=chrome_options)
    actions = ActionChains(browser)
    browser.get(link)
    #=============================================================
    browser.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]').click()
    time.sleep(2)
    browser.find_element(By.CSS_SELECTOR, ".HQzyZ").click()
    # browser.find_element(By.CSS_SELECTOR, ".DVeyrd").click()
    time.sleep(2)
    actions.send_keys(Keys.DOWN).perform()
    time.sleep(0.5)
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(2)
    #=============================================================
    number_of_reviews = int(browser.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[2]/div/div[2]/div[3]').text.split()[0].replace('.', ''))
    
    time.sleep(2)

    file_path = f'{"data_review_crawl"}/{folder_name}/{name}.csv'

    getReviews(browser,number_of_reviews,file_path)


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