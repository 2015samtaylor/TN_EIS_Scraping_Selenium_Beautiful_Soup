#!/usr/bin/env python
# coding: utf-8

# In[6]:

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
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)
from config import username, password

logging.basicConfig(filename='EIS_process.log', level=logging.INFO,
                   format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',force=True)

logging.info('\n\n-------------EIS school error reports log')


# Specify the download directory
download_directory = r"P:\01-GDPST\TN - DAIS\State Reporting\TN\EIS\Exports\EIS\Holding_Dir"  

# Set up Chrome options
chrome_options = webdriver.ChromeOptions()
prefs = {'download.default_directory' : download_directory,
         'profile.default_content_setting_values.automatic_downloads': 1,
         'profile.content_settings.exceptions.automatic_downloads.*.setting': 1}
chrome_options.add_experimental_option('prefs', prefs)

chrome_service = Service(r'C:\Users\samuel.taylor\Desktop\Python_Scripts\EIS\ChromeDriver\chromedriver.exe')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options = chrome_options)
url = 'https://orion.tneducation.net'


# -------------------------------------------------------------------------------
# If it is a 500 error, there is no solution

def get_to_EIS_homepage_with_retry(max_retries=4):
    retries = 0

    while retries < max_retries:
        try:
            # Open the URL in the browser
            driver.get(url)

            # Wait for the overlay to disappear
            overlay = WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, 'orion-loading-overlay'))
            )

            # Wait for the link with id 'linkLogin' to be clickable
            login_link = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, 'linkLogin'))
            )

            # Click on the link
            login_link.click()

            # Wait for login box to appear, and send username
            username_input = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.NAME, 'loginfmt'))
            )
            username_input.send_keys(username)

            submit = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, 'idSIButton9'))
            )

            submit.click()

            # Wait for password input to appear, and send password
            password_input = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.NAME, 'passwd'))
            )
            password_input.send_keys(password)

            submit = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, 'idSIButton9'))
            )

            submit.click()

            # If we've reached this point without exceptions, the function has succeeded
            return

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Retrying...")
            retries += 1
            time.sleep(3)  # Add a delay before retrying

    print(f"Max retries reached ({max_retries}). Function failed.")
    logging.info(f'Max retries reached ({max_retries}). Function failed')
    
    
get_to_EIS_homepage_with_retry(max_retries=4)

# -------------------------------------------Begin Downloads---------------------------------------------------------------
eis_image = '//*[@id="orion-application"]/div[2]/tdoe-sidebar-layout/mat-sidenav-container/mat-sidenav-content/div/div[2]/article/app-orion-application-list/main/div/div/div[2]/app-orion-launch-card/mat-card/div'
data_reports_image = '//*[@id="orion-application"]/div[2]/tdoe-sidebar-layout/mat-sidenav-container/mat-sidenav-content/div/div[2]/article/app-orion-application-list/main/div/div/div[1]/app-orion-launch-card/mat-card/div'


def open_app_select_school(xpaths1, xpaths2, schools1, app_xpath):
    
    window_handles = driver.window_handles
    driver.switch_to.window(window_handles[0])

    #click on image
    span_element = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, app_xpath))
    )

    span_element.click()

    dropdown = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'mat-select-arrow-wrapper'))
    )
    dropdown.click()
    
    
    #Here is where the try except needs to go for when the app is re-launched
    # The x paths change
    
    try:
        school_choice = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//span[@class="mat-option-text" and text()="{}"]'.format(xpaths1)))
        )
        print(f"school_choice element found and clickable through {xpaths1}.")
        school_choice.click()

    except (TimeoutException, NoSuchElementException, NoSuchWindowException, AttributeError) as e:
        print(f"First xpath did not work for school - {schools1}")
        print(f'Trying this xpath {xpaths2}')
        school_choice = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//span[@class="mat-option-text" and text()="{}"]'.format(xpaths2)))
        )
        school_choice.click()

# -------------------------------------------------------------------------------------
def launch_application(xpaths1, xpaths2, schools1, app_choice, max_retries=4, retry_delay=5):
    for retry in range(max_retries):
        try:
            launch_app = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@class="mat-focus-indicator mat-raised-button mat-button-base mat-primary"]/span[text()="Launch Application"]'))
            )

            # Click on the span element
            launch_app.click()

            # --switch to new window once app is launched

            window_handles = driver.window_handles
            driver.switch_to.window(window_handles[-1])
            
            if app_choice == 'EIS':

                district_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.NAME, 'district'))
                )
                district_button.click()
            
            elif app_choice == 'Data_Reports':
            
                research_queries = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="NavigationMenu"]/ul/li[4]/a'))
                )

                research_queries.click()
            
            else:
                print('app variable is wrong')
            

            # If the launch was successful, break out of the retry loop
            break

        except (TimeoutException, NoSuchElementException, NoSuchWindowException, AttributeError) as e:
            print(f'Issue launching app for {schools1}')
            if retry < max_retries - 1:
                # recreate conn with window
                window_handles = driver.window_handles
                driver.switch_to.window(window_handles[0])

                # Navigating back to a previous page
                driver.back()
                
                #The xpaths should be good here as the switching happesn within the func 
                open_app_select_school(xpaths1, xpaths2, schools1, eis_image)

                # Wait before retrying
                time.sleep(retry_delay)
            else:
                print(f'Max retries reached for {schools1}. Giving up.')

                
# -----------------------Download School Error Reports-----------------------------------
                
def download_school_error_reports(xpaths1, schools1, xpaths2):
    
    open_app_select_school(xpaths1, xpaths2, schools1, eis_image)
    

    launch_application(xpaths1, xpaths2, schools1, 'EIS', max_retries=4, retry_delay=5)

    #-----------------In district tab, now submitting form and downloading the file------------------------
    
    submit_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.NAME, 'SUBMIT'))
    )
    submit_button.click()

    #click on dynamic errors button
    dynamic_errors = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.LINK_TEXT, 'Dynamic Errors'))
    )
    dynamic_errors.click()

    go_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/table[3]/tbody/tr/td[2]/table/tbody/tr/td/form/table/tbody/tr/td[2]/a/img'))
    )

    go_button.click()

    # ----------------------------------------------------

    dropdown = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.NAME, 'locat'))
    )
    dropdown.click()

    School_Level_Errors = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/table[3]/tbody/tr/td[2]/table/tbody/tr/td/form/table/tbody/tr/td[2]/select/option[2]'))
    )

    School_Level_Errors.click()

    go_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/table[3]/tbody/tr/td[2]/table/tbody/tr/td/form/table/tbody/tr/td[2]/a/img'))
    )

    go_button.click()

    # in next window now

    dropdown = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.NAME, 'select2'))
    )
    dropdown.click()



    Download_All_School_Errors = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/table[3]/tbody/tr/td[2]/table/tbody/tr/td/form/table/tbody/tr[2]/td[3]/select/option[2]'))
    )

    Download_All_School_Errors.click()


    #Got hung up HERE
    go_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/table[3]/tbody/tr/td[2]/table/tbody/tr/td/form/table/tbody/tr[2]/td[3]/a/img'))
    )
    
    try:
        #download the file
        go_button.click()
        driver.close()   
        logging.info(f'Downloaded {schools1} school error reports')
        
    except Exception as e:
        logging.info(f'Failed to download {schools1} school error reports')
            
    
# ---------------------------------------------Declaring Final Functions and recursive variables-------------------------------------------------

#clean out the directories before the new sends
eis_file_errors_path = r'C:\Users\amy.hardy\Desktop\Python_Scripts\EIS_outputs\EIS File Errors'

def clean_dir(dir_path):
    if os.path.exists(dir_path):
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            else:
                pass
                

def move_files(str_match, final_dest):

    # Move the audits to the other folder. 
    target_dir = pd.DataFrame(os.listdir(download_directory))
    target_dir = target_dir.loc[target_dir[0].str.contains(str_match, case = False)]
    target_dir = target_dir.rename(columns = {0: 'files'})
    
    print(target_dir)
    logging.info(target_dir)
    
    
    # move audit files over to proper directory

    for file in target_dir['files']:
        source_path = os.path.join(download_directory, file)
        destination_path = os.path.join(final_dest, file)

        shutil.move(source_path, destination_path)
        
# ---------------------------Calling the process---------------------------------------

#Directories must be cleaned prior to sending new data
clean_dir(download_directory)
logging.info(f'Download directory cleaned')


school_dict_2 =  {'WDL' : ' School User (Wooddale Middle School - Achievement School District) ',
                    'KRB' : ' School User (Kirby Middle School - Achievement School District) ',
                    'HIL' : ' School User (Hillcrest High School - Achievement School District) ',
                    'BLF' : ' School User (Bluff City High School - Tennessee Public Charter School Commission) ',
                    'FLY' : ' School User (Fairley High School - Achievement School District) '}


school_dict_1 =  {'WDL' : ' SCH (Wooddale Middle School - Achievement School District) ',
                    'KRB' : ' SCH (Kirby Middle School - Achievement School District) ',
                    'HIL' : ' SCH (Hillcrest High School - Achievement School District) ',
                    'BLF' : ' SCH (Bluff City High School - Tennessee Public Charter School Commission) ',
                    'FLY' : ' SCH (Fairley High School - Achievement School District) '}


combined_dict = zip(school_dict_1.items(), school_dict_2.items())

for (schools1, xpaths1), (schools2, xpaths2) in combined_dict:
    download_school_error_reports(xpaths1, schools1, xpaths2)
    
#Since process has ran with no bugs in the downloads, now clear the eis_file_errors dir, and move the files over  
#Must call sleep to give the final download time to get in the directory
time.sleep(15)
clean_dir(eis_file_errors_path)
move_files('AllErr', eis_file_errors_path)
logging.info('EIS file errors downloaded and moved')

