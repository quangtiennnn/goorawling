from tools import *
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

class Goorawling:
    def __init__(self, link, chrome_options=chrome_options):
        self.link = link
        self.driver = webdriver.Chrome(options=chrome_options)
        self.actions = ActionChains(self.driver)

    def open(self):
        self.driver.get(self.link)

    def move_to_all_photos(self):
        move_to_all_photos(self.driver)

    def tag_click(self, tag):
        tag_click(self.driver, tag)

    def get_images(self, file_path):
        get_images(self.driver, file_path)

    def get_restaurant_link(self, restaurant_string):
        return get_restaurant_link(self.driver, restaurant_string)

    def get_reviews(self, number_of_reviews, file_path, constant=0.55, thresh_hold=1000):
        get_reviews(self.driver, number_of_reviews, file_path, constant, thresh_hold)

    def crawl_restaurant(self, restaurant_id, folder_name='sample'):
        images_path = f'{str(folder_name)}/images/{str(restaurant_id)}.csv'
        reviews_path = f'{str(folder_name)}/reviews/{str(restaurant_id)}.csv'
        self.open()
        self.move_to_all_photos()
        self.get_images(images_path)


# goorawler = Goorawling('https://www.google.com/maps/?hl=vi')
# goorawler.open()
# goorawler.move_to_all_photos()
# goorawler.get_images('sample/images/123.csv')
# goorawler.close()