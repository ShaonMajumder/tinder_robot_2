from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
import configparser
import pickle

def loadCookies():
    cookies = None
    with open('cookies.pkl', 'rb') as file:
        cookies = pickle.load(file)
    return cookies

def saveCookies(cookies):
    with open('cookies.pkl', 'wb') as file:
        pickle.dump(cookies, file)

def addCookie(driver,cookies):
    for cookie in cookies:
        driver.add_cookie(cookie)

cookies = None
config = configparser.ConfigParser()
config.read('config.txt')
email = config.get('Credentials', 'email')
password = config.get('Credentials', 'password')
chrome_driver_path = 'resources/drivers/chromedriver'

PRIVACY_TEXT = "We value your privacy."
xpath_query = f'//p[contains(text(), "{PRIVACY_TEXT}")]'
PRIVACY_ACCEPT_BUTTON = '//div[contains(text(), "I accept")]'

# Flow Constant
LOGIN_BUTTON_XPATH = '//div[contains(text(), "Log in")]'
LOGIN_WITH_FACEBOOK_BUTTON_XPATH = '//div[contains(text(), "Log in with Facebook")]'
#Fillup Popup form
EMAIL_TEXTINPUT_XPATH = '//label[contains(text(), "Email address or phone number:")]/following-sibling::input'
PASSWORD_TEXTINPUT_XPATH = '//label[contains(text(), "Password:")]/following-sibling::input'
SUMBIT_BUTTON_NAME = 'login'

SHARE_YOUR_LOCATION_TEXT = '//div[contains(text(), "Share Your Location")]'
LOCATION_SHARING_BUTTON =  '//div[normalize-space()="Allow"]' #'//div[contains(text(), "Allow")]'
ENABLE_NOTIFICATION_TEXT = '//div[contains(text(), "Enable Notifications")]'
NOT_INTERESTED_BUTTON = '//div[contains(text(), "Not interested")]'

YOU_RECEIVED_A_LIKE_TEXT = '//h3[contains(text(), "You Received a Like")]'
MAYBE_LATER_BUTTON = '//div[normalize-space()="Maybe Later"]'
MAIN_CONTAINER_OF_SWAPPING = '//div[@aria-label="Card stack"]'


LIKE_BUTTON = '//span[normalize-space()="Like"]'
NOPE_BUTTON = '//span[normalize-space()="Nope"]'


def ExceptionContainerForPopup(driver):
    driver = locationSharingEnable(driver)
    driver = notificationDecline(driver)
    driver = youReceiveALikePrompt(driver)

def swappinMechanism(driver):
    wait.until(EC.presence_of_element_located((By.XPATH, MAIN_CONTAINER_OF_SWAPPING)))
    matching_elements = driver.find_element('xpath',MAIN_CONTAINER_OF_SWAPPING)
    print('like container ')
    print(matching_elements)
    if matching_elements:
        print(f"The text '{MAIN_CONTAINER_OF_SWAPPING}' exists on the web page.")
        wait.until(EC.presence_of_element_located((By.XPATH, LIKE_BUTTON)))
        like_button = wait.until(EC.element_to_be_clickable((By.XPATH, LIKE_BUTTON)))
        like_button.click()
        print('You liked the person')
        sleep(5)
    else:
        print(f"The text '{MAIN_CONTAINER_OF_SWAPPING}' does not exist on the web page.")
            
    return driver



def youReceiveALikePrompt(driver):
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, YOU_RECEIVED_A_LIKE_TEXT)))
        matching_elements = driver.find_element('xpath',YOU_RECEIVED_A_LIKE_TEXT)
        if matching_elements:
            print(f"The text '{YOU_RECEIVED_A_LIKE_TEXT}' exists on the web page.")
            wait.until(EC.presence_of_element_located((By.XPATH, MAYBE_LATER_BUTTON)))
            maybe_later_button = wait.until(EC.element_to_be_clickable((By.XPATH, MAYBE_LATER_BUTTON)))
            maybe_later_button.click()
            print('Removed received a like prompt')
        else:
            print(f"The text '{YOU_RECEIVED_A_LIKE_TEXT}' does not exist on the web page.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return driver



def locationSharingEnable(driver):
    try:
        matching_elements = driver.find_element('xpath',SHARE_YOUR_LOCATION_TEXT)
        if matching_elements:
            print(f"The text '{SHARE_YOUR_LOCATION_TEXT}' exists on the web page.")
            wait.until(EC.presence_of_element_located((By.XPATH, LOCATION_SHARING_BUTTON)))
            location_allow_button = wait.until(EC.element_to_be_clickable((By.XPATH, LOCATION_SHARING_BUTTON)))
            location_allow_button.click()
            print('Removed Location sharing prompt')
        else:
            print(f"The text '{SHARE_YOUR_LOCATION_TEXT}' does not exist on the web page.")
            
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return driver


def notificationDecline(driver):
    try:
        matching_elements = driver.find_element('xpath',ENABLE_NOTIFICATION_TEXT)
        if matching_elements:
            print(f"The text '{ENABLE_NOTIFICATION_TEXT}' exists on the web page.")
            wait.until(EC.presence_of_element_located((By.XPATH, NOT_INTERESTED_BUTTON)))
            not_interested_button = wait.until(EC.element_to_be_clickable((By.XPATH, NOT_INTERESTED_BUTTON)))
            not_interested_button.click()
            print('Removed Notification prompt')
        else:
            print(f"The text '{ENABLE_NOTIFICATION_TEXT}' does not exist on the web page.")
            
        
    except Exception as e:
        print(f"An error occurred: {e}")
    return driver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f'--webdriver={chrome_driver_path}')
driver = webdriver.Chrome(options=chrome_options)
url = 'https://www.tinder.com'
driver.get(url)

wait = WebDriverWait(driver, 10)


try:
    matching_elements = driver.find_element('xpath',xpath_query)
    if matching_elements:
        print(f"The text '{PRIVACY_TEXT}' exists on the web page.")
        wait.until(EC.presence_of_element_located((By.XPATH, PRIVACY_ACCEPT_BUTTON)))
        accept_button = wait.until(EC.element_to_be_clickable((By.XPATH, PRIVACY_ACCEPT_BUTTON)))
        accept_button.click()
    else:
        print(f"The text '{PRIVACY_TEXT}' does not exist on the web page.")

    
except Exception as e:
    print(f"An error occurred: {e}")







try:
    wait.until(EC.presence_of_element_located((By.XPATH, LOGIN_BUTTON_XPATH)))
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, LOGIN_BUTTON_XPATH)))
    login_button.click()
except Exception as e:
    print(f"An error occurred: {e}")

    
try:
    wait.until(EC.presence_of_element_located((By.XPATH, LOGIN_WITH_FACEBOOK_BUTTON_XPATH)))
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, LOGIN_WITH_FACEBOOK_BUTTON_XPATH)))
    login_button.click()
except Exception as e:
    print(f"An error occurred: {e}")


# Detect the popup window
popup_window_handle = None


# Iterate through window handles to find the popup
for handle in driver.window_handles:
    driver.switch_to.window(handle)
    print("title", driver.title)
    if "Facebook" in driver.title:  # Adjust the title as needed
        popup_window_handle = handle
        print('Login with Facebook Popup found')
        break


email_input = driver.find_element('xpath', EMAIL_TEXTINPUT_XPATH)
password_input = driver.find_element('xpath', PASSWORD_TEXTINPUT_XPATH)
login_button = driver.find_element(By.NAME, SUMBIT_BUTTON_NAME)  # Replace with the actual element locator


email_input.send_keys(email)
password_input.send_keys(password)
login_button.click()

# if popup_window_handle:
driver.switch_to.window(popup_window_handle)
while True:
    try:
        # Check if the current window handle still exists
        driver.switch_to.window(popup_window_handle)
        print('contineu')
    except Exception:
        # The window handle no longer exists, meaning the popup has closed
        print("Popup has closed.")
        driver.switch_to.window(driver.window_handles[0])  # Switch back to the main window
        break


sleep(5)



# cookies = driver.get_cookies()
# print('cookies', cookies)
# saveCookies(cookies)

# cookies = loadCookies()
# cookies = [{'domain': 'tinder.com', 'expiry': 1693637802, 'httpOnly': False, 'name': 'AWSALBCORS', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '4Wk9CXsUvS/TNOZXyqED9WS4FmUQ00Grb8OegQiisH7SBBuhqt47asqnPJXUV4GPJ7KjNBADdSTToaa6oQeOwUP+H5znx9dVpwzxdkkKwoblPQzVwH+NEEenaOXD'}, {'domain': '.tinder.com', 'expiry': 1693637790, 'httpOnly': False, 'name': 'AF_SYNC', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1693032990811'}, {'domain': '.tinder.com', 'expiry': 1727593008, 'httpOnly': False, 'name': 'AF_MEASUREMENT_STATUS', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'true'}, {'domain': '.tinder.com', 'expiry': 1693119389, 'httpOnly': False, 'name': '_gid', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'GA1.2.431384209.1693032989'}, {'domain': '.tinder.com', 'expiry': 1727593008, 'httpOnly': False, 'name': 'afUserId', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'd7e12fa3-ae7b-441c-a24f-be75825509bc-p'}, {'domain': '.tinder.com', 'expiry': 1727592989, 'httpOnly': False, 'name': '_ga', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'GA1.2.1224343956.1693032989'}, {'domain': '.tinder.com', 'expiry': 1727593008, 'httpOnly': False, 'name': 'AF_DEFAULT_MEASUREMENT_STATUS', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'false'}, {'domain': '.tinder.com', 'expiry': 1693033049, 'httpOnly': False, 'name': '_gat_gtag_UA_60214108_5', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1'}, {'domain': '.tinder.com', 'expiry': 1727593015, 'httpOnly': False, 'name': '_ga_CDPT3R4PG7', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'GS1.1.1693032989.1.1.1693033015.0.0.0'}, {'domain': 'tinder.com', 'expiry': 1693637802, 'httpOnly': False, 'name': 'AWSALB', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '4Wk9CXsUvS/TNOZXyqED9WS4FmUQ00Grb8OegQiisH7SBBuhqt47asqnPJXUV4GPJ7KjNBADdSTToaa6oQeOwUP+H5znx9dVpwzxdkkKwoblPQzVwH+NEEenaOXD'}, {'domain': '.tinder.com', 'expiry': 1700808989, 'httpOnly': False, 'name': '_gcl_au', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1.1.705253467.1693032989'}]
# driver = webdriver.Chrome(options=chrome_options)
# driver.get('https://tinder.com')
# addCookie(driver,cookies)
# driver.refresh()

i = 0
while True:
    try:
        driver = swappinMechanism(driver)
    except Exception as e:
        print(f"On Loop An error occurred: {e}")
        driver = ExceptionContainerForPopup(driver)

    print('Loop Step ',i)
    i = i + 1

driver.quit()
