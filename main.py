#-*-coding:utf-8-*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup
import time
import os
import shaonutil

from tinder_utility import *

# usable to alert - driver.switch_to_alert()


# start

if os.path.isfile('private/config.ini'):
	pass
else:
	create_private_folder()

config = shaonutil.file.read_configuration_ini('private/config.ini')
email = config['authentication']['email']
password = config['authentication']['password']

chrome_driver_path = "resources/chromedriver.exe"
driver = webdriver.Chrome(chrome_driver_path)
driver.get("https://tinder.com")

# give time popup to show up
time.sleep(11)

if is_element_exist(driver,"//button/span[text()='Log in']"):
	login_button = driver.find_element_by_xpath("//button/span[text()='Log in']")

# change and make login smother , faster and ensure 100% work time
dialog_box = driver.find_element_by_xpath("//div[@role='dialog']")
close_box = dialog_box.find_element_by_xpath("//button[@aria-label='Close']")
facebook_login_button = driver.find_element_by_xpath("//button/span[text()='Log in with Facebook']")

try:
	login_button.click()
	print("Clicked login_button")
	facebook_login_button.click()
except:
	facebook_login_button.click()

facebook_login_popup(driver,email,password)

if 'tinder.com' in driver.current_url:
	print('Returned to '+driver.current_url)

time.sleep(2)

if 'tinder.com/app/recs' in driver.current_url:
	print('login_granted')

share_ur_location_xpath = "//div[@id=\"onboarding-description\" and contains(text(),\"Tinder uses your location to find people around you\")]"
if is_element_exist(driver,share_ur_location_xpath):
	driver.find_element_by_xpath("//button[@type=\"button\" and @aria-label=\"Allow\"]/span[text()=\"Allow\"]").click()
	print("Enabled location permission.")

#time.sleep(4)

notification_xpath = "//div[@id=\"onboarding-description\" and text()=\"Get notifications about new matches or messages.\"]"
if is_element_exist(driver,notification_xpath):
	driver.find_element_by_xpath("//button[@type=\"button\" and @aria-label=\"Not interested\"]/span[text()=\"Not interested\"]").click()
	print("Cancelled notifications permission.")
