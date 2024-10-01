from add_parent_to_sys_path import add_parent_to_sys_path
add_parent_to_sys_path()
import os
import logging
from config import username, password
from modules.selenium_process import *
from modules.file_modifications import *
from datetime import datetime
current_date = datetime.now()
date_string = current_date.strftime('%Y-%m-%d')

# Create logs directory if it doesn't exist
clear_logging_handlers()
log_dir = '../logs'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(filename=os.path.normpath(os.path.join(log_dir, 'EIS_adm_audit_student_membership_log')),
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    force=True)
logging.info('\n\n-------------EIS adm audit student membership log')


download_directory = os.path.join(os.getcwd(), 'outputs' , date_string)
sftp_path = r'S:\SFTP\EIS'
url = 'https://orion.tneducation.net'


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

try:
    root_dir = os.path.dirname(download_directory)
    stack_files_send_to_SFTP(root_dir, sftp_path, 'ADMAudit')
except ValueError:
    logging.info('Files were not downloaded there is nothing to stack')

try:
    stack_files_send_to_SFTP(root_dir, sftp_path, 'StudentMembership')
except ValueError:
    logging.info('Files were not downloaded there is nothing to stack')


#Fix batch file paths