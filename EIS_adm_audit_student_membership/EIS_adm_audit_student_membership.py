from add_parent_to_sys_path import add_parent_to_sys_path
add_parent_to_sys_path()

import os
import logging
from datetime import datetime
from config import *
from modules.selenium_process import *
from modules.file_modifications import *

# Set up logging
clear_logging_handlers()
log_dir = '../logs'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.normpath(os.path.join(log_dir, 'EIS_adm_audit_student_membership_log.log')),
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    force=True
)
logging.info('\n\n-------------EIS adm audit student membership log')

# Paths
current_date = datetime.now()
date_string = current_date.strftime('%Y-%m-%d')
download_directory = os.path.join(os.getcwd(), 'outputs', date_string)
sftp_path = r'S:\SFTP\EIS'
url = 'https://orion.tneducation.net'



def selenium_process(which_school, username, password):
    try:
        # Set Chrome options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = chrome_binary_path

        # Set download preferences
        prefs = {
            'download.default_directory': download_directory,
            'profile.default_content_setting_values.automatic_downloads': 1,
            'profile.content_settings.exceptions.automatic_downloads.*.setting': 1
        }
        chrome_options.add_experimental_option('prefs', prefs)

        # Initialize WebDriver
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logging.info(f'ChromeDriver initialized successfully for {which_school}')

        # Navigate and download files
        get_to_EIS_homepage_with_retry(username, password, driver, url, max_retries=4)
        get_adm_audit_student_membership_loop(driver, which_school)
        wait_for_cr_files(download_directory, sleep_time=10)

    except Exception as e:
        logging.error(f'Error processing {which_school}: {str(e)}')

    finally:
        # Quit WebDriver to free resources
        try:
            driver.quit()
            logging.info(f'Closed WebDriver for {which_school}')
        except Exception as e:
            logging.error(f'Error quitting WebDriver for {which_school}: {e}')


# Create and clean directories
make_dir(download_directory)
clean_dir(download_directory)

# Run processes for both schools
selenium_process('ASD', username_asd, password_asd)
selenium_process('BLF', username_blf, password_blf)

#Stack & Send files to SFTP
for report in ['ADMAudit', 'StudentMembership']:
    try:
        send_to_SFTP(download_directory, sftp_path, report)
        logging.info(f'Successfully sent {report} to SFTP')
    except ValueError:
        logging.info(f'No files to send for {report}')
