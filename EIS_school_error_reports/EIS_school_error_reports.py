from add_parent_to_sys_path import add_parent_to_sys_path
add_parent_to_sys_path()
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os
import pandas as pd
import logging
from config import username, password
from modules.selenium_process import *
from modules.file_modifications import *

# Create logs directory if it doesn't exist
clear_logging_handlers()
log_dir = '../logs'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(filename=os.path.normpath(os.path.join(log_dir, 'EIS_school_error_reports')),
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    force=True)
logging.info('\n\n-------------EIS school error reports log')


download_directory = os.path.join(os.getcwd(), 'outputs' , 'downloads')
sftp_path = r'S:\SFTP\EIS'
url = 'https://orion.tneducation.net'


# Set up Chrome options
try:
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        'download.default_directory':download_directory,
        'profile.default_content_setting_values.automatic_downloads': 1,
        'profile.content_settings.exceptions.automatic_downloads.*.setting': 1
    }
    chrome_options.add_experimental_option('prefs', prefs)

    # Specify the path to the manually downloaded ChromeDriver
    chrome_driver_path = r"C:\Program Files\chromedriver-win64\chromedriver.exe"
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    logging.info('ChromeDriver initialized successfully')

except Exception as e:
    logging.error(f'Error initializing ChromeDriver: {str(e)}')


#Create and clean our directories prior to sending new data
make_dir(download_directory)
clean_dir(download_directory)

get_to_EIS_homepage_with_retry(username, password, driver, url, max_retries=4)

for (schools1, xpaths1), (schools2, xpaths2) in combined_dict:
    download_school_error_reports(xpaths1, schools1, xpaths2, driver)

wait_for_cr_files(download_directory, sleep_time=10)
try:
    driver.quit() #once files have been downloaded driver is good to close out
    logging.info('Quiting driver')
except Exception as e:
    logging.info(f'Unable to quit driver due to {e}')

try:
    stack_files_send_to_SFTP(download_directory, sftp_path, 'AllErr')
except ValueError:
    logging.info('Files were not downloaded there is nothing to stack')