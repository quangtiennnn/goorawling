from tools import *

def move_to_all_photos(driver):
    driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[26]/div[2]/div[2]/div[2]/div[1]/button').click()

def tag_click(tag):
    driver.find_element(By.XPATH, f'//div[contains(@class, "Gpq6kf") and contains(@class, "NlVald") and text()="{tag}"]').click()

def get_images_by_tags(driver):
    # Get all tag names except 'All' and 'Latest' :)
    elems = driver.find_elements(By.CSS_SELECTOR, '.Gpq6kf.NlVald')
    tag_names = [elem.text for elem in elems if elem.text != 'All' and elem.text != 'Latest']

    tag_images = {}

    for tag in tag_names:
        try:
            tag_click(tag)
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
            
    return tag_images








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
        all_button = driver.find_element(By.XPATH, '//button[contains(@class, "K4UgGe") and @aria-label="All"]')
        
        actions.move_to_element(all_button).perform() # Move to the button and click it!!!
        time.sleep(random.uniform(1, 3))

        all_button.click()

        get_images_by_tags(driver)


