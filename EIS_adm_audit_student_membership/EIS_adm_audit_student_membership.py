from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException
from bs4 import BeautifulSoup
import os
import time
import pandas as pd
import shutil
import logging
import time
import sys

# Add the parent directory to the Python path to get username, and password
current_dir = os.getcwd()
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)

from config import username, password
from EIS_school_error_reports.modules.selenium_process import *
from EIS_school_error_reports.modules.file_modifications import *


logging.basicConfig(filename='EIS_process.log', level=logging.INFO,
                   format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',force=True)
logging.info('\n\n-------------EIS adm audit student membership log')


download_directory = os.path.join(os.getcwd(), 'outputs' , 'downloads')
sftp_path = r'S:\SFTP\EIS'
url = 'https://orion.tneducation.net'

# Set up Chrome options
chrome_options = webdriver.ChromeOptions()
prefs = {'download.default_directory' : download_directory,
         'profile.default_content_setting_values.automatic_downloads': 1,
         'profile.content_settings.exceptions.automatic_downloads.*.setting': 1}
chrome_options.add_experimental_option('prefs', prefs)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options = chrome_options)


#Create and clean out directories
make_dir(download_directory)
clean_dir(download_directory)


get_to_EIS_homepage_with_retry(username, password, driver, url, max_retries=4)
get_adm_audit_student_membership_loop(driver)


wait_for_cr_files(download_directory, sleep_time=10)
try:
    driver.quit() #once files have been downloaded driver is good to close out
    logging.info('Quiting driver')
except Exception as e:
    logging.info(f'Unable to quit driver due to {e}')


stack_files_send_to_SFTP(download_directory, sftp_path, 'ADMAudit')
stack_files_send_to_SFTP(download_directory, sftp_path, 'StudentMembership')