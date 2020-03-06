from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from PIL import Image
import mysql.connector as mysql
from cvmodels import *

import time
import os
import wget
import re
import string
import secrets
import uuid
import shaonutil
import sys


folders = {
	'private_folder' : 'private/',
    'images_folder' : 'private/data/',
    'face_found_image_path' : "private/data/faces/",
    'face_not_found_image_path' : "private/data/not_faces/"
}

# mysql-connector-python
# mysql_connector_repackaged
column_info = {
	'candidate_sid':'VARCHAR(255)',
	'candidate_name':'VARCHAR(255)',
	'candidate_age':'VARCHAR(255)',
	'candidate_distance':'VARCHAR(255)',
	'candidate_living_place':'VARCHAR(255)',
	'candidate_university_or_instituition':'VARCHAR(255)',
	'candidate_image_webp_url':'TEXT(1000)',
	'candidate_unique_image_name':'VARCHAR(255)',
	'candidate_detected_faces':'VARCHAR(255)',
	'candidate_detection_alogorithm_name':'VARCHAR(255)',
	'candidate_detected_confidences':'VARCHAR(255)'
}



def append_tupple(values,next_value):
	return tuple(list(values) + [next_value])

def sleep(timeout, retry=3):
	def the_real_decorator(function):
		def wrapper(*args, **kwargs):
			retries = 0
			while retries < retry:
				if retries > 0:
					print("Retrying ...")
				try:
					value = function(*args, **kwargs)
					if value is None:
						return
				except:
					print(f'Sleeping for {timeout} seconds')
					time.sleep(timeout)
					retries += 1
					if retries == retry:
						raise MaxTryOver("Max retry is over.")
		return wrapper
	return the_real_decorator

def convert_to_jpg(image_filename):
	im = Image.open(image_filename).convert("RGB")
	jpeg_filename = ''.join(image_filename.split('.')[:-1]) + '.jpg'
	im.save(jpeg_filename,"jpeg")
	os.remove(image_filename)
	return jpeg_filename

class MaxTryOver(Exception):
	"""docstring for ClassName"""
	def __init__(self, *args):
		if args:
			self.message = args[0]
		else:
			self.message = None

	def __str__(self):
		print("calling string")
		if self.message:
			return 'Error >> {0} '.format(self.message)
		else:
			return 'MaxTryOverError has been raised.'

class ButtonNotFound(Exception):
	"""docstring for ClassName"""
	def __init__(self, *args):
		if args:
			self.message = args[0]
		else:
			self.message = None

	def __str__(self):
		print("calling string")
		if self.message:
			return 'Error >> {0} '.format(self.message)
		else:
			return 'ButtonNotFoundError has been raised.'

	
class tinderbot:
	def __init__(self,driver):
		self.driver = driver
		self.value_init()

	def __repr__(self):
		return "TinderBot(browser) at "+self.driver.current_url
	
	def __str__(self):
		return self.driver.current_url

	def set_db_config(self,dbconfig):
		self.dbconfig = dbconfig
		
	def initialize_db(self):
		dbname = self.dbconfig['database']
		tbname = self.dbconfig['table']

		db = mysql.connect(
			host = self.dbconfig['host'],
			user = self.dbconfig['user'],
			passwd = self.dbconfig['password'],
		)

		cursor = db.cursor()
		cursor.execute("SHOW DATABASES")
		databases = cursor.fetchall()
		databases = [x[0] for x in databases]
		if dbname not in databases:
			print("Creating database "+dbname+" ...")
			cursor.execute("CREATE DATABASE "+dbname)

		db = mysql.connect(
			host = self.dbconfig['host'],
			user = self.dbconfig['user'],
			passwd = self.dbconfig['password'],
			database = self.dbconfig['database']
		)

		cursor = db.cursor()
		cursor.execute('SHOW TABLES')
		tables = cursor.fetchall()
		if tbname not in [ x[0] for x in tables ]:
			print("Creating table "+tbname+" ...")
			cursor.execute("CREATE TABLE "+self.dbconfig['table']+" (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,"+''.join([' '+info+' '+column_info[info]+',' for info in column_info])[:-1]+")")
	
	def insert_data(self,value):
		dbname = self.dbconfig['database']
		tbname = self.dbconfig['table']
		# candidate_name, candidate_age, candidate_distance, candidate_living_place, candidate_university_or_instituition, candidate_image_webp_url, candidate_unique_image_name
		#cursor.execute("DESC "+tbname)
		query = "INSERT INTO "+tbname+ ' (' + ''.join([key+', ' for key in column_info])[:-2] + ') VALUES ('+ ''.join(['%s, ' for key in column_info])[:-2]  +')'

		## storing values in a variable
		values = [
		    value
		]

		db = mysql.connect(
			host = self.dbconfig['host'],
			user = self.dbconfig['user'],
			passwd = self.dbconfig['password'],
			database = self.dbconfig['database']
		)
		cursor = db.cursor()

		## executing the query with values
		cursor.executemany(query, values)

		## to make final output we have to run the 'commit()' method of the database object
		db.commit()

		print(cursor.rowcount, "record inserted")

	def list_data(self):
		db = mysql.connect(
			host = self.dbconfig['host'],
			user = self.dbconfig['user'],
			passwd = self.dbconfig['password'],
			database = self.dbconfig['database']
		)
		cursor = db.cursor()

		query = "SELECT * FROM "+self.dbconfig['database']

		## getting records from the table
		cursor.execute(query)

		## fetching all records from the 'cursor' object
		records = cursor.fetchall()

		## Showing the data
		for record in records:
		    print(record)

	def drop_database(self):
		dbname = self.dbconfig['database']
		db = mysql.connect(
			host = self.dbconfig['host'],
			user = self.dbconfig['user'],
			passwd = self.dbconfig['password'],
		)
		cursor = db.cursor()
		cursor.execute("DROP DATABASE "+dbname)

	def create_configuration(self):
		print('Getting your configurations to save it.\n')
		print('Facebook configurations -')
		fbemail = input('Give your fb email : ')
		fbpassword = input('Give your fb password : ')
		print('\nDatabase configurations -')
		dbhost = input('Give your db host : ')
		dbuser = input('Give your db user : ')
		dbpassword = input('Give your db password : ')
		dbname = input('Give your db name : ')
		dbtable = input('Give your db table : ')

		f = open("private/config.ini", "w+")
		f.writelines(["; config file\n", "[fb_authentication]\n", "email = "+fbemail+"\n", "password = "+fbpassword+"\n", "[db_authentication]\n", "host = "+dbhost+"\n", "user = "+dbuser+"\n", "password = "+dbpassword+"\n", "database = "+dbname+"\n", "table = "+dbtable+"\n"])
		f.close()

	def value_init(self):
		self.profile_info = ''
		self.background_images_urls = ''
		self.downloaded_profile_images = ''
		self.unique_profile_image_file_names = ''

		self.temp_image = 'my_screenshot.jpg'
		self.unique_profile_image_file_name = ''
		self.unique_sid = ''

	
	def parse_profile_info(self):
		driver = self.driver
		root_container = '//div[contains(@class,"recsCardboard__cardsContainer")]'
		intermediate_identifier = '//div[contains(@class,"active") and contains(@class,"recCard")]'
		info_container = '//div[contains(@class,"recCard__info")]'

		Name_xpath       = root_container+intermediate_identifier+info_container+'/div[1]/div/div/span'
		Age_xpath        = root_container+intermediate_identifier+info_container+'/div[1]/div/span'

		#get them as list
		list_type_info_xpath = root_container+intermediate_identifier+info_container+'/div[2]/div/div/div'
		Job_xpath        = root_container+intermediate_identifier+info_container+'/div[2]/div/div/div[1]/div[2]'
		Ins_xpath        = root_container+intermediate_identifier+info_container+'/div[2]/div/div/div[2]/div[2]'
		location_xpath   = root_container+intermediate_identifier+info_container+'/div[2]/div/div/div[3]/div[2]'
		distant_xpath    = root_container+intermediate_identifier+info_container+'/div[2]/div/div/div[4]/div[2]'

		image_file = root_container+'/div[1]/div[2]/div[1]/div/div/div/div/div'

		Name = driver.find_element_by_xpath(Name_xpath).text
		Age = driver.find_element_by_xpath(Age_xpath).text

		list_type_info_xpath = root_container+intermediate_identifier+info_container+'/div[2]/div/div/div'
		list_type_infos = driver.find_elements_by_xpath(list_type_info_xpath)
		list_type_infos = [info.text for info in list_type_infos]

		distance_bool = True
		living_place_bool = True
		distance = ''
		living_place = ''
		university_or_instituition = []

		for info in list_type_infos:
			if 'kilometers away' in info or 'kilometer away' in info and distance_bool:
				distance = re.sub("[^0-9]", "", info)
				distance_bool = False
			elif 'Lives in ' in info and living_place_bool:
				living_place = info.replace('Lives in ','')
				living_place_bool = False
			else:
				university_or_instituition.append(info)
			# rest is university or instituition

		
		#backgrounds = driver.find_elements_by_xpath('//div[@class="Bdrs(8px) Bgz(cv) Bgp(c) StretchedBox"]')
		#background = backgrounds[1]
		#background_style_string = background.get_attribute('style')
		#first_sub,second_sub = 'background-image: url\("','"\)'
		#matches = re.findall(r''+first_sub+'(.+?)'+second_sub,background_style_string)
		#image_webp_url = matches[0]
		image_webp_urls = self.get_background_images_urls()


		university_or_instituition = "'"+str(university_or_instituition)+"'"

		Sid = self.get_unique_profile_sid()

		self.profile_info = Sid, Name, Age, distance, living_place, university_or_instituition, image_webp_urls
		return Sid, Name, Age, distance, living_place, university_or_instituition, image_webp_urls

	def get_background_images_urls(self):
		browser = self.driver

		#make image active
		root_container = '//div[contains(@class,"recsCardboard__cardsContainer")]'
		image_navigation_buttons_container = root_container + '/div[1]/div[3]/div[1]/div[2]/button'
		buttons = browser.find_elements_by_xpath(image_navigation_buttons_container)
		images_container = root_container+'/div[1]/div[3]/div[1]/div[1]/div/div'
		images = browser.find_elements_by_xpath(images_container)

		if len(buttons) == len(images):
			images_url = [images_container +'['+str(i)+']/div/div' for i in range(1,len(images)+1)]

			while True:
				try:
					image_webp_urls = []
					for i in range(0,len(buttons)):
						# make image active
						buttons[i].click()
						background_style_string = browser.find_element_by_xpath(images_url[i]).get_attribute('style')
						#if background_style_string == '' : break
						print("string "+background_style_string)
						first_sub,second_sub = 'background-image: url\("','"\)'
						matches = re.findall(r''+first_sub+'(.+?)'+second_sub,background_style_string)
						image_webp_urls.append(matches[0])
					break
				except:
					pass

			# return to initials
			buttons[0].click()

		self.background_images_urls = image_webp_urls
		return image_webp_urls

	def download_profile_images(self):
		#and convert to jpg
		image_webp_urls = self.profile_info[6]
		print("found "+str(len(image_webp_urls))+" profile images")
		# downloading
		image_webp_filenames = []
		for image_webp_url in image_webp_urls:
			ext = image_webp_url.split('.')[-1]
			image_webp_filename = image_webp_url.split('/')[-1]
			wget.download(image_webp_url,image_webp_filename)
			image_webp_filenames.append(image_webp_filename)
			print("Downloading Image "+image_webp_filename+" ...")
		
		# converting
		converted_jpgs = []
		for image_webp_filename in image_webp_filenames:
			ext = image_webp_filename.split('.')[-1]
			if ext != 'jpg':
				print("Image extension is "+ext+", Converting to jpg")
				converted_jpg_filename = convert_to_jpg(image_webp_filename)
			else:
				converted_jpg_filename = image_webp_filename
			converted_jpgs.append(converted_jpg_filename)
		self.downloaded_profile_images = converted_jpgs
		return converted_jpgs

	def download_profile_image(self):
		image_webp_url = self.profile_info[6]
		ext = image_webp_url.split('.')[-1]
		image_webp_filename = self.temp_image.split('.',1)[0] + "." + ext
		wget.download(image_webp_url,image_webp_filename)
		print("Downloading Image "+image_webp_filename+" ...")
		if ext != 'jpg':
			print("Image extension is "+ext+", Converting to jpg")
			im = Image.open(image_webp_filename).convert("RGB")
			im.save(self.temp_image,"jpeg")
			os.remove(image_webp_filename)

	def get_unique_profile_sid(self):
		db = mysql.connect(
			host = self.dbconfig['host'],
			user = self.dbconfig['user'],
			passwd = self.dbconfig['password'],
			database = self.dbconfig['database']
		)

		cursor = db.cursor()

		unique_sid = generateCryptographicallySecureRandomString(8)

		while True:
			print("Generating unique_sid for profile...")
			query = "SELECT * FROM "+self.dbconfig['table']+" WHERE `candidate_sid` = '"+unique_sid+"'"

			## getting records from the table
			cursor.execute(query)

			## fetching all records from the 'cursor' object
			records = cursor.fetchall()

			## Showing the data
			for record in records:
			    print(record)


			if(len(records)>1):
				unique_sid = generateCryptographicallySecureRandomString(8)
			else:
				break
		self.unique_sid = unique_sid
		return unique_sid


	def get_local_unique_profile_image_file_name(self):
		
		db = mysql.connect(
			host = self.dbconfig['host'],
			user = self.dbconfig['user'],
			passwd = self.dbconfig['password'],
			database = self.dbconfig['database']
		)

		cursor = db.cursor()

		image_file_name = self.temp_image
		ext = image_file_name.split('.')[-1]
		unique_name = generateCryptographicallySecureRandomString(8) + '.' + ext

		while True:
			print("Generating unique_name for image...")
			query = "SELECT * FROM candidates WHERE `candidate_unique_image_name` = '"+unique_name+"'"

			## getting records from the table
			cursor.execute(query)

			## fetching all records from the 'cursor' object
			records = cursor.fetchall()

			## Showing the data
			for record in records:
			    print(record)


			if(len(records)>1):
				unique_name = generateCryptographicallySecureRandomString(8) + '.' + ext
			else:
				break
		self.unique_profile_image_file_name = unique_name
		return unique_name

	def get_local_unique_profile_image_file_names(self):
		profile_images = self.downloaded_profile_images
		
		
		db = mysql.connect(
			host = self.dbconfig['host'],
			user = self.dbconfig['user'],
			passwd = self.dbconfig['password'],
			database = self.dbconfig['database']
		)
		
		cursor = db.cursor()

		image_file_name = self.temp_image
		ext = image_file_name.split('.')[-1]
		unique_name = generateCryptographicallySecureRandomString(8) + '.' + ext

		store_uniques = []
		for profile_image in profile_images:
			while True:
				print("Generating unique_name for image...")
				query = "SELECT * FROM candidates WHERE `candidate_unique_image_name` = '"+unique_name+"'"

				## getting records from the table
				cursor.execute(query)

				## fetching all records from the 'cursor' object
				records = cursor.fetchall()

				## Showing the data
				for record in records:
				    print(record)


				if(len(records)>1):
					unique_name = generateCryptographicallySecureRandomString(8) + '.' + ext
					print("matched with previously downloaded image name")
				else:
					if unique_name not in store_uniques:
						store_uniques.append(unique_name)
						break
					else:
						unique_name = generateCryptographicallySecureRandomString(8) + '.' + ext
						print("matched with recently downloaded image name")

		self.unique_profile_image_file_names = store_uniques
		return store_uniques

	def rename_image_unique(self):
		os.rename(self.temp_image,self.unique_profile_image_file_name)	
		return self.unique_profile_image_file_name
	def rename_image_uniques(self):
		downloaded_images = self.downloaded_profile_images
		unique_images = self.unique_profile_image_file_names

		if len(downloaded_images) != len(unique_images):
			raise ValueError("len(downloaded_images) != len(unique_images)")
		
		print(zip(downloaded_images,unique_images))

		for d,u in zip(downloaded_images,unique_images):
			print("Renamed "+d+" to "+u+" ...")
			os.rename(d,u)

		return unique_images
		
	def parse_detect_swipe(self):
		browser = self.driver
		#Name, Age, distance, living_place, university_or_instituition, image_webp_urls = tb.parse_profile_info()
		core_values = self.parse_profile_info()
		*core_values_ , image_webp_urls = core_values
		core_values = tuple( core_values_ + [str(image_webp_urls)] )

		downloaded_profile_images = self.download_profile_images()
		self.get_local_unique_profile_image_file_names()
		unique_names = self.rename_image_uniques()
		

		#for unique_name in unique_names:
		# for each image there is a unique file name, that means for a specific person if it has multiple images, then we have multiple records
		for unique_name in unique_names:
			print(unique_name)
			faces,algorithm_name,confidence_list = try_detect_face_algorithms(unique_name)
			print(faces,algorithm_name,confidence_list)

			values = append_tupple(core_values,unique_name)
			values = append_tupple(values,faces)
			values = append_tupple(values,algorithm_name)
			values = append_tupple(values,str(confidence_list))

			self.insert_data(values)
			move(unique_name,folders['images_folder']+unique_name)

		# all value to ''
		self.value_init()


def try_push_like(browser,If_not_reached_limit):
    
    while True:
        if If_not_reached_limit == False:
                break
        try:
            wait = WebDriverWait(browser, 1)
            like_box = wait.until(EC.visibility_of_element_located((By.XPATH, '//button[@type="button" and @aria-label="Like"]')))
            like_box.click()
            print("Liked")
            break
        except TimeoutException:
            print("Trying to check the like div")
            pass
        except WebDriverException:
            #if daily like limit exceed
            If_not_reached_limit = not if_like_limit_reached(browser)
    
    return If_not_reached_limit

def generateSecureRandomString(stringLength=10):
    """Generate a secure random string of letters, digits and special characters """
    password_characters = string.ascii_letters + string.digits #+ string.punctuation
    return ''.join(secrets.choice(password_characters) for i in range(stringLength))

def generateCryptographicallySecureRandomString(stringLength=10):
	randomString = uuid.uuid4().hex.upper() # get a random string in a UUID fromat
	randomString  = randomString[0:stringLength]
	return randomString






def is_element_exist(driver,xpath,timeout=5):
	wait = WebDriverWait(driver, timeout)
	try:
		wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
		return True
	except TimeoutException:
		return False



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

def detect_facebook_popup_login_page(driver):
	html_source = driver.page_source
	soup = BeautifulSoup(html_source, 'html.parser')
	htmlTagdic = get_attribute_dic_from_tag(html_source,'html')
	titleTagdic = get_attribute_dic_from_tag(html_source,'title')
	
	if 'id' in htmlTagdic and 'id' in titleTagdic:
		if htmlTagdic['id'] == 'facebook' and  titleTagdic['id'] == 'pageTitle' and soup.find('title').text == 'Facebook' and 'www.facebook.com' in driver.current_url:
			return True
		else:
			return False


def facebook_login_popup(driver,email,password):
	window_before = driver.window_handles[0]
	window_after = driver.window_handles[1]
	
	driver.switch_to.window(window_after)

	if detect_facebook_popup_login_page(driver):
		print('in facebook login popup')
		driver.find_element_by_xpath("//input[@type=\"text\" and @name=\"email\" and @id=\"email\"]").send_keys(email)
		driver.find_element_by_xpath("//input[@type=\"password\" and @name=\"pass\" and @id=\"pass\"]").send_keys(password)
		driver.find_element_by_xpath("//input[@id=\"u_0_0\" and @name=\"login\" and @value=\"Log In\" and @type=\"submit\"]").click()

		print("Waiting for authentication...")
		# if window is open and auth url is not reach
		checkpoint_det = False
		while check_window_open(driver,window_after):
			# after 3 minute quit application
			current_url = driver.current_url
			if current_url != None:
				if current_url.find('https://www.facebook.com/checkpoint/?next=https://www.facebook.com/v2.8/dialog/oauth'):
					if not checkpoint_det:
						print("Waiting at checkpoint for 2 factor authentication or anything else.")
						checkpoint_det = True
				elif current_url.find('https://www.facebook.com/v2.8/dialog/oauth'):
					print("Clear indication of authentication achieved...")
					break
			"""
			final url
			https://www.facebook.com/v2.8/dialog/oauth?app_id=464891386855067&cbt=1582871222240&channel_url=https%3A%2F%2Fstaticxx.facebook.com%2Fconnect%2Fxd_arbiter.php%3Fversion%3D45%23cb%3Dfc8650e497c20c%26domain%3Dtinder.com%26origin%3Dhttps%253A%252F%252Ftinder.com%252Ff59fc770251c4%26relation%3Dopener&client_id=464891386855067&display=popup&domain=tinder.com&e2e=%7B%7D&fallback_redirect_uri=https%3A%2F%2Ftinder.com%2F&locale=en_US&logger_id=f23c1e8e96e255&origin=1&redirect_uri=https%3A%2F%2Fstaticxx.facebook.com%2Fconnect%2Fxd_arbiter.php%3Fversion%3D45%23cb%3Dff86373397156%26domain%3Dtinder.com%26origin%3Dhttps%253A%252F%252Ftinder.com%252Ff59fc770251c4%26relation%3Dopener%26frame%3Df1048ca586e6988&response_type=token%2Csigned_request%2Cgraph_domain&scope=user_birthday%2Cuser_photos%2Cemail%2Cuser_friends%2Cuser_likes&sdk=joey&version=v2.8&ret=login&fbapp_pres=0

			https://www.facebook.com/v2.8/dialog/oauth?app_id=464891386855067&cbt=1582871222240&channel_url=https://staticxx.facebook.com/connect/xd_arbiter.php?version=45#cb=fc8650e497c20c&domain=tinder.com&origin=https%3A%2F%2Ftinder.com%2Ff59fc770251c4&relation=opener&client_id=464891386855067&display=popup&domain=tinder.com&e2e={}&fallback_redirect_uri=https://tinder.com/&locale=en_US&logger_id=f23c1e8e96e255&origin=1&redirect_uri=https://staticxx.facebook.com/connect/xd_arbiter.php?version=45#cb=ff86373397156&domain=tinder.com&origin=https%3A%2F%2Ftinder.com%2Ff59fc770251c4&relation=opener&frame=f1048ca586e6988&response_type=token,signed_request,graph_domain&scope=user_birthday,user_photos,email,user_friends,user_likes&sdk=joey&version=v2.8&ret=login&fbapp_pres=0
			"""

		# save_cookie()		
		driver.switch_to.window(window_before)
	else:
		print('not facebook')

def get_attribute_dic_from_tag(html_source,tag_name):
	soup = BeautifulSoup(html_source, 'html.parser')
	tag_obj = soup.find(tag_name)
	valdic = {k:v for k,v in zip([a for a in tag_obj.attrs],list(tag_obj.attrs.values()))}
	return valdic

def wait_to_find(xpath_):
	while True:
		try:
			object_ = driver.find_element_by_xpath(xpath_)
			return object_
		except:
			time.sleep(1)