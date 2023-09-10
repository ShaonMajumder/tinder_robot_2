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
import cv2 
import mysql.connector
import os
import cvmodels


IMAGE_FOLDER_PATH = 'extracted_images'

cookies = None
config = configparser.ConfigParser()
config.read('config.txt')
email = config.get('Credentials', 'email2')
password = config.get('Credentials', 'password2')
dbhost = config.get('Database', 'dbhost')
dbuser = config.get('Database', 'dbuser')
dbpassword = config.get('Database', 'dbpassword')
dbname = config.get('Database', 'dbname')

chrome_driver_path = 'resources/drivers/chromedriver'

# xpath vars
PRIVACY_TEXT = "We value your privacy."
xpath_query = f'//p[contains(text(), "{PRIVACY_TEXT}")]'
PRIVACY_ACCEPT_BUTTON = '//div[contains(text(), "I accept")]'
######
# Flow Constant
LOGIN_BUTTON_XPATH = '//div[contains(text(), "Log in")]'
LOGIN_WITH_FACEBOOK_BUTTON_XPATH = '//div[contains(text(), "Log in with Facebook")]'
#Fillup Popup form
EMAIL_TEXTINPUT_XPATH = '//label[contains(text(), "Email address or phone number:")]/following-sibling::input'
PASSWORD_TEXTINPUT_XPATH = '//label[contains(text(), "Password:")]/following-sibling::input'
SUMBIT_BUTTON_NAME = 'login'
######
SHARE_YOUR_LOCATION_TEXT = '//div[contains(text(), "Share Your Location")]'
LOCATION_SHARING_BUTTON =  '//div[normalize-space()="Allow"]' #'//div[contains(text(), "Allow")]'
ENABLE_NOTIFICATION_TEXT = '//div[contains(text(), "Enable Notifications")]'
NOT_INTERESTED_BUTTON = '//div[contains(text(), "Not interested")]'
######
YOU_RECEIVED_A_LIKE_TEXT = '//h3[contains(text(), "You Received a Like")]'
MAYBE_LATER_BUTTON = '//div[normalize-space()="Maybe Later"]'
MAIN_CONTAINER_OF_SWAPPING = '//div[@aria-label="Card stack"]'

## //div[@aria-hidden="false" and @data-keyboard-gamepad="true"] //span[contains(@class, "keen-slider__slide")] //div[@role="img"]
ACTIVE_CARD = '//div[@aria-hidden="false" and @data-keyboard-gamepad="true"]'
ACTIVE_SLIDER_IMAGES_CONTAINER = f'{ACTIVE_CARD} //span[contains(@class, "keen-slider__slide")]'
ACTIVE_SLIDER_IMAGES_BUTTON_CONTAINER = f'{ACTIVE_CARD} //div[contains(@class, "CenterAlign")]'
ACTIVE_SLIDER_IMAGES_BUTTONS_XPATH = f'{ACTIVE_CARD} //div[contains(@class, "CenterAlign")] //button[contains(@class, "bullet")]'
IMAGES_DIV = f'{ACTIVE_CARD} //span[contains(@class, "keen-slider__slide")] //div[@role="img"]'
######
# MAIN_CONTAINER_OF_SWAPPING = '//div[contains(@class, "recsCardboard__cardsContainer")]'
LIKE_BUTTON = '//span[normalize-space()="Like"]'
NOPE_BUTTON = '//span[normalize-space()="Nope"]'
# MAIN_CONTAINER_OF_SWAPPING = LIKE_BUTTON #'//div[contains(@class, "recsCardboard__cards")]'
XPATH_VERIFIED_BADGE = '//*[text()="Verified!"]'
XPATH_UNIVERSITY = "//div[@itemprop='affiliation']"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f'--webdriver={chrome_driver_path}')
driver = webdriver.Chrome(options=chrome_options)
url = 'https://www.tinder.com'
driver.get(url)

wait = WebDriverWait(driver, 10)

## //div[@aria-hidden="false" and @data-keyboard-gamepad="true"] //span[contains(@class, "keen-slider__slide")] //div[@role="img"]
ACTIVE_CARD = '//div[@aria-hidden="false" and @data-keyboard-gamepad="true"]'
ACTIVE_SLIDER_IMAGES_CONTAINER        = f'{ACTIVE_CARD} //span[contains(@class, "keen-slider__slide")]'
IMAGES_DIV                            = f'{ACTIVE_CARD} //span[contains(@class, "keen-slider__slide")] //div[@role="img"]'
ACTIVE_SLIDER_IMAGES_BUTTON_CONTAINER = f'{ACTIVE_CARD} //div[contains(@class, "CenterAlign")]'
ACTIVE_SLIDER_IMAGES_BUTTONS_XPATH    = f'{ACTIVE_CARD} //div[contains(@class, "CenterAlign")] //button[contains(@class, "bullet")]'
XPATH_AGE = f'{ACTIVE_CARD} //span[@itemprop="age"]'
XPATH_NAME = f'{ACTIVE_CARD} //span[@itemprop="name"]'
XPATH_DISTANCE = f'{ACTIVE_CARD} //div[contains(text(), "kilometers away")]'
XPATH_PASSIONS = f'{ACTIVE_CARD} //div[contains(@class, "background-passions-inactive-overlay")]'

def detectFace(image_path):
    image = cv2.imread(image_path)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # cv2.imshow('Detected Faces', image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    cv2.imwrite(image_path, image)



    
def getName(driver):
    try:
        name_element = driver.find_element(By.XPATH, XPATH_NAME)
        name = name_element.text
        return name
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def getAge(driver):
    try:
        age_element = driver.find_element(By.XPATH, XPATH_AGE)
        age = age_element.text
        return age
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def getDistance(driver):
    try:
        distance_element = driver.find_element(By.XPATH, XPATH_DISTANCE)
        distance = distance_element.text
        distance_match = re.search(r'(\d+)', distance)
        if distance_match:
            distance = distance_match.group(0)
            return distance
        else:
            print("Distance not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def getPassions(driver):
    try:
        print('getting passions')
        passions_element = driver.find_elements(By.XPATH, XPATH_PASSIONS)
        passions_text_array = [element.text for element in passions_element]
        passions_text_array = ','.join(passions_text_array)
        print(f'getting passions {passions_text_array}')
        return passions_text_array
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def isVerifiedProfile(driver):
    try:
        verified = driver.find_element(By.XPATH, XPATH_VERIFIED_BADGE)
        return True if len(verified) == 1 else False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
def getUniversity(driver):
    try:
        age_element = driver.find_element(By.XPATH, XPATH_UNIVERSITY)
        age = age_element.text
        return age
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
         
def saveInfoToDB(name, age, distance, university, passions, is_me_liked, images_number, isVerified):
    try:
        table_name = 'persons'
        connection = mysql.connector.connect(
            host=dbhost,
            user=dbuser,
            password=dbpassword,
            database=dbname
        )
        cursor = connection.cursor()
        query = f"INSERT INTO {table_name} (name, age, distance, university, passions, is_me_liked, images_number, is_verified) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (name, age, distance, university, passions, is_me_liked, images_number, isVerified)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        print("information saved to the database successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def getLastInsertedPersonId():
    table_name = 'persons'
    try:
        with mysql.connector.connect(
            host=dbhost,
            user=dbuser,
            password=dbpassword,
            database=dbname
        ) as connection:
            cursor = connection.cursor()
            query = f"SELECT id FROM {table_name} ORDER BY id DESC LIMIT 1"
            cursor.execute(query)
            last_id = cursor.fetchone()
            cursor.close()
            if last_id is not None:
                return last_id[0]
            else:
                return -1
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return -1
    
def createFolderIfNotExists(IMAGE_FOLDER_PATH):
    if not os.path.exists(IMAGE_FOLDER_PATH):
        try:
            os.makedirs(IMAGE_FOLDER_PATH)
            print(f"Folder '{IMAGE_FOLDER_PATH}' created successfully.")
        except OSError as e:
            print(f"Error creating folder '{IMAGE_FOLDER_PATH}': {str(e)}")

def swappinMechanism(driver, like):
    if like :
        wait.until( EC.presence_of_element_located((By.XPATH, LIKE_BUTTON)))
        like_button = wait.until(EC.element_to_be_clickable((By.XPATH, LIKE_BUTTON)))
        like_button.click()
        print('You liked the person')
    else:
        wait.until( EC.presence_of_element_located((By.XPATH, NOPE_BUTTON)))
        like_button = wait.until(EC.element_to_be_clickable((By.XPATH, NOPE_BUTTON)))
        like_button.click()
        print('You dislike the person')
    return driver

def downloadMysqlBackup(backup_file_path):
    try:
        connection = mysql.connector.connect(
            host=dbhost,
            user=dbuser,
            password=dbpassword,
            database=dbname
        )
        cursor = connection.cursor()
        with open(backup_file_path, 'w') as backup_file:
            cursor.execute(f"BACKUP DATABASE {dbname} TO '{backup_file_path}'")
        print(f"Backup completed. The SQL backup file is saved as '{backup_file_path}'.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def downloadImageRoutine():
    driver.switch_to.window(driver.current_window_handle)
    createFolderIfNotExists(IMAGE_FOLDER_PATH)
    last_person_id = getLastInsertedPersonId()
    last_person_id = 0 if last_person_id == -1 else last_person_id
    last_person_id = last_person_id + 1
    name = ''
    age = ''
    distance = ''
    passions = ''
    verified = None
    university = ''
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
            if not name:
                name = getName(driver)
            if not age:
                age = getAge(driver)
            if not distance:
                distance = getDistance(driver)
            if not passions:
                passions = getPassions(driver)
            if not verified:
                verified = isVerifiedProfile(driver)
            if not university:
                university = getUniversity(driver)
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
                                        image_link = f'{IMAGE_FOLDER_PATH}/image-{last_person_id}-{image_number}.jpg'
                                        img.save(image_link, 'JPEG')  # Use f-string to include i in the filename
                                        # detectFace(image_link)
                                        print(f"WebP image converted to JPG successfully. {image_link}.jpg")
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
    
    liked = False
    if expected_number_of_images > 2:
        liked = True
    else:
        liked = False
    swappinMechanism(driver, liked)
    saveInfoToDB(name, age, distance, university, passions, liked, expected_number_of_images, verified)