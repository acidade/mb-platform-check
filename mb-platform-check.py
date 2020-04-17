### IMPORT ###
from requests import get
from bs4 import BeautifulSoup
import time
import datetime
import json
import random
import credentials as credentials
from notifiers import get_notifier
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
from time import sleep
print("-- Importing libraries done --")

### Load Selenium and set options to be headless
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
print("-- Selenium started --")

### SETTINGS & SETUP ###
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
urls = ['https://stock.mercedes-benz.swiss','https://occasion.mercedes-benz.swiss','https://stock.mercedes-benz.swiss/vans','https://occasion.mercedes-benz.swiss/vans']
# how to mark missing values
missing = "none"

#initiate empty list
error_log=[]
log=[]

# set start time and timestamp
print("-- Everything set, starting scraping --")
time_start = time.time()
timestamp_started = datetime.datetime.fromtimestamp(time_start).strftime('%d.%m.%Y, %H:%M:%S')
file_timestamp = datetime.datetime.fromtimestamp(time_start).strftime('%Y%m%d%H%M')


#### function SCRAPING ####
def scrape_site(urls):
	total_offers = 0
	time_start = time.time()
	timestamp_started = datetime.datetime.fromtimestamp(time_start).strftime('%d.%m.%Y, %H:%M:%S')
	# open Selenium, go to website and get results
	driver = webdriver.Chrome('chromedriver', options=options)

	# Loop through URLs
	for url in urls:
		driver.get(url)
		#waitforit = WebDriverWait(driver,15).until(EC.presence_of_element_located((By.ID, "modeltabs")))

		sleep(5)
		soup = BeautifulSoup(driver.page_source, 'html.parser')
		print('\n==============================================================================')
		print(f'-- Page {url} retrieved, starting parser and linkcheck --')

		#print(soup)

		offers = 0
		vehicles = []
		error = False
		for entry in soup.find_all('div', {'class': 'model-info'}):
			try:
				model = entry.find('h3').text.strip()
				count = entry.find('div', {'class': 'v-btn__content'}).text.strip()
				count = int(count.replace(" Angebote anzeigen", ""))
				offers = offers + count
				print(f'{model}: {count}')
			except:
				print('Something went wrong. Counter not found.')
				error = True
		if not error:
			print(f'{offers} Offers found on URL "{url}"')
		if offers == 0:
			inform_telegram(offers, url, timestamp_started)
		total_offers = total_offers + offers
		print('==============================================================================')

	print(f'-- Scraping done in {time.time()-time_start} seconds --')
	inform_telegram(total_offers, 'All platforms', timestamp_started)
	
	# Cleaning up
	try:
		driver.quit()
		print('-- Driver quit --')
	except:
		print('Error: Quitting driver was not possible.')
#### #### #### #### #### ####


#### function INFORM TELEGRAM CHANNEL ####
def inform_telegram(offers, url, timestamp_started):
	#print(f'Telegram msg-sent placeholder: {offers} offers found on {url}')
	#return None
	#try:
	# create message
	message = f'--- {offers} Offers ---\nURL: {url}\nStarted: {timestamp_started}'

	#send message
	telegram = get_notifier('telegram')
	telegram_status = telegram.notify(message=message, token=credentials.bot_token, chat_id=credentials.chat_id)
	print(f'Successfully informed Telegram channel: {telegram_status}')
	#except:
	#	print(f'Error while informing Telegram channel: {telegram_status}')
#### #### #### #### #### ####


#### function WRITE JSON FILE ####
def write_json(filename, list):
	try:
		with open(filename, 'w') as json_file:  
			json.dump(list, json_file)
		print(f'Success: JSON file "{filename}" written.')
	except:
		print(f'Fail: Writing JSON file "{filename}" failed.')
#### #### #### #### #### ####


scrape_site(urls)


