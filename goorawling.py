from tools import *


###################
class Goorawling:
    def __init__(self, link):
        self.link = link

    def run(self):
        driver = webdriver.Chrome(options=chrome_options)
        actions = ActionChains(driver)
        driver.get(self.link)

        ## Click on the "All" button to show all photos
        actions = ActionChains(driver)
        all_button = driver.find_element(By.XPATH, '//button[contains(@class, "K4UgGe") and @aria-label="Tất cả"]')

        actions.move_to_element(all_button).perform() # Move to the button and click it!!!
        time.sleep(random.uniform(1, 3))

        all_button.click()

        # get_images_by_tags(driver)


