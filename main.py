#-*-coding:utf-8-*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from shutil import copyfile,move
from bs4 import BeautifulSoup
from tinder_utility import *
import time
import os
import shaonutil

# usable to alert - browser.switch_to_alert()
folders = {
	'private_folder' : 'private/',
    'images_folder' : 'private/data/',
    'face_found_image_path' : "private/data/faces/",
    'face_not_found_image_path' : "private/data/not_faces/"
}

def try_creating_folders():
	for folder in folders:
		folder = folders[folder]
		if not os.path.exists(folder):
			os.mkdir(folder)
			print("Creating folder "+folder+" ...")

try_creating_folders()


chrome_driver_path = "resources/drivers/chromedriver.exe"
browser = webdriver.Chrome(chrome_driver_path)

tb = tinderbot(browser)



if os.path.isfile('private/config.ini'):
	print("Configurations found !")	
else:
	print("Creating configurations ...")
	tb.create_configuration('gui')


config = shaonutil.file.read_configuration_ini('private/config.ini')
email = config['fb_authentication']['email']
password = config['fb_authentication']['password']

dbhost = config['db_authentication']['host']
dbuser = config['db_authentication']['user']
dbpasswd = config['db_authentication']['password']
dbname = config['db_authentication']['database']
tbname = config['db_authentication']['table']

tb.set_db_config({
	'host' : dbhost,
	'user' : dbuser,
	'password' : dbpasswd,
	'database' : dbname,
	'table' : tbname
})

tb.initialize_db()

# change and make login smother , faster and ensure 100% work time

# give time popup to show up
exit_c = False

@sleep(3,retry=3)
def finding_app_login_by_facebook():
	browser.get("https://tinder.com")
	if is_element_exist(browser,"//button/span[text()='Log in']",11):
		login_button = browser.find_element_by_xpath("//button/span[text()='Log in']")

	try:
		login_button.click()
		print("Clicked login_button")
	except:
		#login_button is not clickable
		#is_element_exist(browser,"//div[@role='dialog']",11)
		#dialog_box = browser.find_element_by_xpath("//div[@role='dialog']")
		#close_box = dialog_box.find_element_by_xpath("//button[@aria-label='Close']")
		pass

	if is_element_exist(browser,"//button/span[text()='Log in with Facebook']",11):
		try:
			facebook_login_button = browser.find_element_by_xpath("//button/span[text()='Log in with Facebook']")
			facebook_login_button.click()
		except:
			browser.find_element_by_xpath('//button[text()="More Options"]').click()
			facebook_login_button = browser.find_element_by_xpath("//button/span[text()='Log in with Facebook']")
			facebook_login_button.click()
			
		exit_c = False
	else:
		raise ButtonNotFound("Facebook login button not found or Site is not reachable")
		exit_c = True
		

#retry 3 times, after 1 time say reloading...,  then browser.quit() quit() to end the program
finding_app_login_by_facebook()


if exit_c:
	browser.quit()
	quit()
	
facebook_login_popup(browser,email,password)

print('Returned to '+browser.current_url)

#time.sleep(2)
now = 0
retry = 30 # for total 10 second max wait
while now < retry:
	if 'tinder.com/app' in browser.current_url:
		print('login_granted')
		break
	time.sleep(0.33) # one third of second
	now += 1


# handling permission dialogues
share_ur_location_xpath = "//div[@id=\"onboarding-description\" and contains(text(),\"Tinder uses your location to find people around you\")]"
if is_element_exist(browser,share_ur_location_xpath,44):
	browser.find_element_by_xpath("//button[@type=\"button\" and @aria-label=\"Allow\"]/span[text()=\"Allow\"]").click()
	print("Enabled location permission.")

else:
	print("location not appread yet")

notification_xpath = "//div[@id=\"onboarding-description\" and text()=\"Get notifications about new matches or messages.\"]"
if is_element_exist(browser,notification_xpath):
	browser.find_element_by_xpath("//button[@type=\"button\" and @aria-label=\"Not interested\"]/span[text()=\"Not interested\"]").click()
	print("Cancelled notifications permission.")
else:
	print("notifications not appread yet")

#@sleep(3,retry=3)
def is_tinder_is_ready_for_swipping(browser):
	print("Checking is tinder is ready for swipping...")
	try:
		#click messages
		browser.find_element_by_xpath('//button[@role="tab" and @id="messages-tab" and @aria-controls="matchListWithMessages" and text()="Messages"]').click()
		#click matches
		browser.find_element_by_xpath('//button[@role="tab" and @id="match-tab" and @aria-controls="matchListNoMessages" and text()="Matches"]').click()
		browser.find_element_by_xpath('//div[contains(@class,"active") and contains(@class,"recCard")]').click()
		return True
	except:
		# not clickable
		return False

# check if tinder is ready for swipping
maxtry = 30
now = 0
while not is_tinder_is_ready_for_swipping(browser) and now < maxtry:
	time.sleep(0.33)
	now += 1



print("Waiting for finishing swipe animation... 4 sec")
time.sleep(4)

tb.parse_detect_swipe()

#store_classfying_image(faces,algorithm_name,temp_image_name)

"""
use unique image name
object and image detection, make decision:
	move image to decision folder
	check if likable or any prompt appread or out of like appeeard
	if out of like the log and quit
	else:
		try liking
		else disliking
"""

#driver.close(), closes the browser window
#driver.quit, closes the driver
browser.close()
browser.quit()