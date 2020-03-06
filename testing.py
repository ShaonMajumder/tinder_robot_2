from tinder_utility import *

chrome_driver_path = "resources/drivers/chromedriver.exe"
browser = webdriver.Chrome(chrome_driver_path)

tb = tinderbot(browser)

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
