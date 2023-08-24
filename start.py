from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import configparser


config = configparser.ConfigParser()
config.read('config.txt')
email = config.get('Credentials', 'email')
password = config.get('Credentials', 'password')


chrome_driver_path = 'resources/drivers/chromedriver'



# Flow Constant
LOGIN_BUTTON_XPATH = '//div[contains(text(), "Log in")]'
LOGIN_WITH_FACEBOOK_BUTTON_XPATH = '//div[contains(text(), "Log in with Facebook")]'
#Fillup Popup form
EMAIL_TEXTINPUT_XPATH = '//label[contains(text(), "Email address or phone number:")]/following-sibling::input'
PASSWORD_TEXTINPUT_XPATH = '//label[contains(text(), "Password:")]/following-sibling::input'
SUMBIT_BUTTON_NAME = 'login'

'//input[contains(text(), "Log in")]'


PRIVACY_TEXT = "We value your privacy."
xpath_query = f'//p[contains(text(), "{PRIVACY_TEXT}")]'
PRIVACY_ACCEPT_BUTTON = '//div[contains(text(), "I accept")]'

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
        print(f"The text '{target_text}' does not exist on the web page.")
        
    
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
    if "Facebook Login" in driver.title:  # Adjust the title as needed
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

# try:
#     WebDriverWait(driver, 0).until_not(EC.title_contains("Facebook Login"))  # Wait until the title doesn't contain "Facebook Login"
#     print("Popup has closed.")
#     driver.switch_to.window(driver.window_handles[0])
# except Exception as e:
#     print(f"An error occurred while waiting for the popup to close: {e}")


sleep(60)

# After logging in, switch back to the main window
driver.switch_to.window(driver.window_handles[0])

# Keep the program running for 60 seconds (or as needed)
sleep(60)

# Close the browser when done (or comment out this line to keep it open)
driver.quit()
