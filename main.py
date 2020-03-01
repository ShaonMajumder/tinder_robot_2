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
# usable to alert - driver.switch_to_alert()

def is_element_exist(driver,xpath):
	wait = WebDriverWait(driver, 5)
	try:
		wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
		return True
	except TimeoutException:
		return False

def create_private_folder():
	os.makedirs('private')
	print('Getting your configurations to save it.')
	email = input('Give your email : ')
	password = input('Give your password : ')

	f = open("private/config.ini", "w+")
	f.writelines(["; config file\n", "[authentication]\n", "email = "+email+"\n", "password = "+password+"\n"])
	f.close()

def check_window_open(driver,window):
	if window in driver.window_handles:
		return True
	else:
		return False


def check_window_open_(driver):
	closed_window_msg = 'no such window: target window already closed'
	if driver.get_log('driver') == []:
		return True
	elif driver.get_log('driver') != []:
		print(driver.get_log('driver'))
		print(driver.get_log('driver') == [])
		print(driver.get_log('driver') == '[]')
		if closed_window_msg in driver.get_log('driver')[-1]['message']:
			return False

def get_attribute_dic_from_tag(html_source,tag_name):
	soup = BeautifulSoup(html_source, 'html.parser')
	tag_obj = soup.find(tag_name)
	valdic = {k:v for k,v in zip([a for a in tag_obj.attrs],list(tag_obj.attrs.values()))}
	return valdic


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


def wait_to_find(xpath_):
	while True:
		try:
			object_ = driver.find_element_by_xpath(xpath_)
			return object_
		except:
			time.sleep(1)

# give time popup to show up
time.sleep(11)
#is_element_exist(driver,"//button/span[text()='Log in']")
login_button = wait_to_find("//button/span[text()='Log in']")
dialog_box = driver.find_element_by_xpath("//div[@role='dialog']")
close_box = dialog_box.find_element_by_xpath("//button[@aria-label='Close']")
facebook_login_button = driver.find_element_by_xpath("//button/span[text()='Log in with Facebook']")

try:
	login_button.click()
	print("Clicked login_button")
	facebook_login_button.click()
except:
	facebook_login_button.click()

def facebook_login_popup(driver):
	window_before = driver.window_handles[0]
	window_after = driver.window_handles[1]
	driver.switch_to.window(window_after)

	
	def detect_facebook_popup_login():
		html_source = driver.page_source
		soup = BeautifulSoup(html_source, 'html.parser')
		htmlTagdic = get_attribute_dic_from_tag(html_source,'html')
		titleTagdic = get_attribute_dic_from_tag(html_source,'title')

		if 'id' in htmlTagdic and 'id' in titleTagdic:
			if htmlTagdic['id'] == 'facebook' and  titleTagdic['id'] == 'pageTitle' and soup.find('title').text == 'Facebook' and 'www.facebook.com' in driver.current_url:
				return True
			else:
				return False

	if detect_facebook_popup_login():
		print('in facebook')
		driver.find_element_by_xpath("//input[@type=\"text\" and @name=\"email\" and @id=\"email\"]").send_keys(email)
		driver.find_element_by_xpath("//input[@type=\"password\" and @name=\"pass\" and @id=\"pass\"]").send_keys(password)
		driver.find_element_by_xpath("//input[@id=\"u_0_0\" and @name=\"login\" and @value=\"Log In\" and @type=\"submit\"]").click()

		#while check_window_open(driver):
		#	pass

		print("Waiting for authentication...")
		# if window is open and auth url is not reach
		while check_window_open(driver,window_after):
			if 'https://www.facebook.com/v2.8/dialog/oauth' in driver.current_url:
				print("clear indication of authentication achieved...")
				break
			
			"""
			final url
			https://www.facebook.com/v2.8/dialog/oauth?app_id=464891386855067&cbt=1582871222240&channel_url=https%3A%2F%2Fstaticxx.facebook.com%2Fconnect%2Fxd_arbiter.php%3Fversion%3D45%23cb%3Dfc8650e497c20c%26domain%3Dtinder.com%26origin%3Dhttps%253A%252F%252Ftinder.com%252Ff59fc770251c4%26relation%3Dopener&client_id=464891386855067&display=popup&domain=tinder.com&e2e=%7B%7D&fallback_redirect_uri=https%3A%2F%2Ftinder.com%2F&locale=en_US&logger_id=f23c1e8e96e255&origin=1&redirect_uri=https%3A%2F%2Fstaticxx.facebook.com%2Fconnect%2Fxd_arbiter.php%3Fversion%3D45%23cb%3Dff86373397156%26domain%3Dtinder.com%26origin%3Dhttps%253A%252F%252Ftinder.com%252Ff59fc770251c4%26relation%3Dopener%26frame%3Df1048ca586e6988&response_type=token%2Csigned_request%2Cgraph_domain&scope=user_birthday%2Cuser_photos%2Cemail%2Cuser_friends%2Cuser_likes&sdk=joey&version=v2.8&ret=login&fbapp_pres=0

			https://www.facebook.com/v2.8/dialog/oauth?app_id=464891386855067&cbt=1582871222240&channel_url=https://staticxx.facebook.com/connect/xd_arbiter.php?version=45#cb=fc8650e497c20c&domain=tinder.com&origin=https%3A%2F%2Ftinder.com%2Ff59fc770251c4&relation=opener&client_id=464891386855067&display=popup&domain=tinder.com&e2e={}&fallback_redirect_uri=https://tinder.com/&locale=en_US&logger_id=f23c1e8e96e255&origin=1&redirect_uri=https://staticxx.facebook.com/connect/xd_arbiter.php?version=45#cb=ff86373397156&domain=tinder.com&origin=https%3A%2F%2Ftinder.com%2Ff59fc770251c4&relation=opener&frame=f1048ca586e6988&response_type=token,signed_request,graph_domain&scope=user_birthday,user_photos,email,user_friends,user_likes&sdk=joey&version=v2.8&ret=login&fbapp_pres=0

			"""

		
		driver.switch_to.window(window_before)
		
		if 'tinder.com' in driver.current_url:
			print('Returned to '+driver.current_url)

		#time.sleep(2)

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
		
		

	else:
		print('not facebook')

facebook_login_popup(driver)
