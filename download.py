### console
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
import configparser
import pickle
import re
import requests
from io import BytesIO
from PIL import Image
from selenium.common.exceptions import StaleElementReferenceException

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f'--webdriver={chrome_driver_path}')
driver = webdriver.Chrome(options=chrome_options)
url = 'https://www.tinder.com'
driver.get(url)

wait = WebDriverWait(driver, 10)

## //div[@aria-hidden="false" and @data-keyboard-gamepad="true"] //span[contains(@class, "keen-slider__slide")] //div[@role="img"]
ACTIVE_SLIDER_IMAGES_CONTAINER        = '//div[@aria-hidden="false" and @data-keyboard-gamepad="true"] //span[contains(@class, "keen-slider__slide")]'
IMAGES_DIV                            = '//div[@aria-hidden="false" and @data-keyboard-gamepad="true"] //span[contains(@class, "keen-slider__slide")] //div[@role="img"]'
ACTIVE_SLIDER_IMAGES_BUTTON_CONTAINER = '//div[@aria-hidden="false" and @data-keyboard-gamepad="true"] //div[contains(@class, "CenterAlign")]'
ACTIVE_SLIDER_IMAGES_BUTTONS_XPATH    = '//div[@aria-hidden="false" and @data-keyboard-gamepad="true"] //div[contains(@class, "CenterAlign")] //button[contains(@class, "bullet")]'


def downloadImageRoutine():
    keen_slider_slides_buttons = driver.find_elements('xpath',ACTIVE_SLIDER_IMAGES_BUTTONS_XPATH)
    expected_number_of_images = len(keen_slider_slides_buttons)
    print(f"expecting {expected_number_of_images} images")
    while True:
        i = 0
        image_number = 0
        unique_urls = set()
        for keen_slider_slides_button in keen_slider_slides_buttons:
            sleep(1)
            keen_slider_slides_button.click() #ok
            try:
                images_div_elements = driver.find_elements('xpath', IMAGES_DIV)
                n = len(images_div_elements)
                # print(f"Image Div length {n}")
                if n > 0:
                    for image in images_div_elements:
                        # print("writing style")
                        try:
                            style_text = image.get_attribute("style")
                        except StaleElementReferenceException:
                            print("Stale element reference while getting style. Skipping this element.")
                            continue
                        url_match = re.search(r'url\("(.*?)"\)', style_text)
                        if url_match:
                            background_url = url_match.group(1)
                            # print(background_url)
                            if background_url not in unique_urls:
                                unique_urls.add(background_url)
                                response = requests.get(background_url)
                                if response.status_code == 200:
                                    webp_data = BytesIO(response.content)
                                    with Image.open(webp_data) as img:
                                        img.save(f'output{image_number}.jpg', 'JPEG')  # Use f-string to include i in the filename
                                        print(f"WebP image converted to JPG successfully. output{image_number}.jpg")
                                        image_number = image_number + 1
                                else:
                                    print("Failed to download the image.")
                        else:
                            print("URL not found in the CSS rule.")
            except StaleElementReferenceException:
                print("Stale element reference while iterating through images. Skipping this element.")
            i = i + 1
        if expected_number_of_images == image_number:
            print(f"accurately downloaded all image_number {image_number}")
            break


for slide in keen_slider_slides:
    print(slide.text) 