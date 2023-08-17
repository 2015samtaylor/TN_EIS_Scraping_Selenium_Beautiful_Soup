#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8

# In[6]:

from sqlalchemy import create_engine
import urllib
import sqlalchemy
import pyodbc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import time
import pandas as pd
from gspread_pandas import Spread, Client
import gspread_pandas
import shutil
import logging

logging.basicConfig(filename='EIS_process.log', level=logging.INFO,
                   format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',force=True)


# Specify the download directory
download_directory = r"P:\Knowledge Management\State Reporting\TN\EIS\Exports\EIS\EIS File Errors"  

# Set up Chrome options
chrome_options = webdriver.ChromeOptions()
prefs = {'download.default_directory' : download_directory,
         'profile.default_content_setting_values.automatic_downloads': 1,
         'profile.content_settings.exceptions.automatic_downloads.*.setting': 1}
chrome_options.add_experimental_option('prefs', prefs)

chrome_service = Service(os.getcwd() + '\\ChromeDriver\\chromedriver.exe')
driver = webdriver.Chrome(service = chrome_service, options=chrome_options)
url = 'https://orion.tneducation.net/unauthorized'

username = 'eduardo.ruedas@tneducation.net'
password = 'wTeT6u7o&^@F'



def get_to_EIS_homepage():
    # Open the URL in the browser
    driver.get(url)

    try:
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

        #Wait for login box to appear, and send username
        username_input = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.NAME, 'loginfmt'))
        )
        username_input.send_keys(username)


        submit = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, 'idSIButton9'))
        )

        submit.click()

        #Wait for password input to appear, and send password
        password_input = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.NAME, 'passwd'))
        )
        password_input.send_keys(password)


        submit = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.ID, 'idSIButton9'))
        )

        submit.click()

        #click on EIS image
        span_element = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="orion-application"]/div[2]/tdoe-sidebar-layout/mat-sidenav-container/mat-sidenav-content/div/div[2]/article/app-orion-application-list/main/div/div/div[2]/app-orion-launch-card/mat-card/div'))
        )


        span_element.click()

        launch_app = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@class="mat-focus-indicator mat-raised-button mat-button-base mat-primary"]/span[text()="Launch Application"]'))
        )

        # Click on the span element
        launch_app.click()



    except Exception as e:
        logging.info(f'An error occured on the homepage login {e}')

#----------------------------------------------------------------------------------------------------------------------


def scrape_student_data():

    # Get the list of window handles
    window_handles = driver.window_handles

    # # Switch to the new window
    new_window_handle = window_handles[-1]
    driver.switch_to.window(new_window_handle)

    student_lookup = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/table[3]/tbody/tr/td[1]/table/tbody/tr[5]/td/a'))
    )
    student_lookup.click()



    # For loop starts here. 
    # read in frame, and get ones that are not done yet. 
    
    c = gspread_pandas.conf.get_config(conf_dir=os.getcwd(), file_name='google_secret.json')
    spread = Spread('SSID Lookup', config=c)

    # Read data from an Excel sheet
    df = spread.sheet_to_df(index = 1, sheet='23-24')   
    
    #TEMPORARY TESTING 
    #df = df.iloc[0:10]
    
     # Identify new names added into the sheet. 
    df = df.loc[(df['Done'] == 'FALSE') & (df['search_results_provided'] == '')]
    
    #Only reading the first 10 columns
    df = df.iloc[:, :10]
    df = df.reset_index()
    #cleaning
    df['first_name'] = df['first_name'].fillna('')
    df['last_name'] = df['last_name'].fillna('')
    df['ssn'] = df['ssn'].replace('', 0)
    #make sure ssn it an int so it can be recognized by if statement
    df['ssn'] = df['ssn'].astype(int)
    

    df_list = []

    for index, row in df.iterrows():
        f_name = row['first_name']
        l_name = row['last_name']
        ssn = row['ssn']
        dob = row['dob']

        SSN = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.NAME, 'SSN'))
            )

        last_name = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.NAME, 'LST_NAME'))
            )

        first_name = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.NAME, 'FST_NAME'))
            )
        
        b_day = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.NAME, 'DOB'))
            )
        
        # if there is a SSN rely on that first. 
        if not pd.isna(ssn) and ssn != 0:

            SSN.clear()
            SSN.send_keys(ssn)

            last_name.clear()

            first_name.clear()
            
            b_day.clear()

        else:

            SSN.clear()

            last_name.clear()
            last_name.send_keys(l_name)

            first_name.clear()
            first_name.send_keys(f_name)
            
            #send keys for birthday right now
            b_day.clear()
            b_day.send_keys(dob)


        go_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="form1"]/table/tbody/tr[13]/td[2]/a/img'))
        )

        go_button.click()

        # ------------------------Beautiful Soup Portion, scraping the HTML for proper data, append to data_list-----------

        # Step 3: Use Selenium to get the page source
        page_source = driver.page_source

        # Step 4: Use BeautifulSoup to parse the page source and extract the data
        soup = BeautifulSoup(page_source, 'html.parser')


        # Identify the tr tags, by their unique quality bgcolor
        parent_element = soup.find_all("tr", bgcolor={"#FAFAD2", "#FFFFFF"})  # Replace with a relevant selector

        try:
            # tag the last one, & strip out the improper date
            td_elements = parent_element[-1]

            # Find all <td> elements within the last parent element
            td_elements = td_elements.find_all('td')

            # Extract the text content from the first 7 <td> elements
            td_texts = [td.get_text(strip=True) for td in td_elements[:8]]
            
        except IndexError:
            
            if not pd.isna(ssn) and ssn != 0:

                td_texts = [[l_name + ',' + f_name + ' '+  '|N']]
                
            else:
                td_texts = [[l_name + ',' + f_name + ' '+  '|N']]


        df_list.append(td_texts)
        driver.back()
        
    column_names = ['eis_name', 'ssid', 'ssn', 'dob', 'gender', 'ethnicity_race', 'tos', 'grade']

    # pd.DataFrame(df_list).head(30)
    frame = pd.DataFrame(df_list, columns= column_names)
    
    # Define the regular expression pattern
    pattern = r'(.*?)(n/a|x{1,})(\d*)'

    # Extract the desired values from the column
    frame['ssn'] = frame['ssn'].str.extract(pattern)[0]
    frame['eis_pin'] = frame['ssn'].str.extract(pattern)[2]
    
    return(frame, df)


def create_columns():

    # Convert the column of lists into strings, and create the 'social or other' column
    frame['eis_name'] = frame['eis_name'].apply(lambda lst: ', '.join(map(str, lst)) if isinstance(lst, list) else lst)

    # The Ns present are the no matches, otherwise filled with a Y
    frame['search_results_provided'] = frame['eis_name'].str.split('|', expand = True)[1]    
    frame['search_results_provided'] = frame['search_results_provided'].fillna('Y')

    # create a temp frame on a merge, to see if ssn was available. Then apply to the frame via new column 'social used'

    temp = frame.merge(df, left_index=True, right_index=True)

    # Custom function to check if social is used 
    def social_used(value):
        if value != 0 and not pd.isnull(value):
            return 'Y'
        else:
            return 'N'

    # Apply the custom function to create a new column
    frame['social_used'] = temp['ssn_y'].apply(social_used)
    
    
def clean_frame_and_rearrange(frame):
    
    # Remove the social or other from EIS name column
    frame['eis_name'] = frame['eis_name'].str.split('|').str[0]
    frame['eis_name'] = frame['eis_name'].str.replace('\xa0', '')   
    

    split_columns = frame['eis_name'].str.split(',', expand = True)

    # # Rename the new columns as needed
    split_columns.rename(columns={0: 'eis_last_name', 1: 'eis_first_name', 2: 'eis_middle_name', 3: 'eis_other'}, inplace=True)
    split_columns = split_columns[['eis_last_name', 'eis_first_name']]

    frame = pd.concat([frame, split_columns], axis=1)

    # get the original first_name, & last_name next to EIS versions
    frame = pd.concat([frame, df[['first_name', 'last_name']]], axis = 1)
    
    #split the white space from the columns
    frame['eis_first_name'] = frame['eis_first_name'].str.strip()
    frame['eis_last_name'] = frame['eis_last_name'].str.strip()

    frame['first_name_match'] = frame['first_name'].str.lower() == frame['eis_first_name'].str.lower()
    frame['last_name_match'] = frame['last_name'].str.lower() == frame['eis_last_name'].str.lower()
    
    
    #declare type of match in match column
    frame.loc[(frame['first_name_match'] == False) & (frame['last_name_match'] == True), 'match'] = 'first name mismatch'
    frame.loc[(frame['first_name_match'] == True) & (frame['last_name_match'] == False), 'match'] = 'last name mismatch'

    frame.loc[(frame['first_name_match'] == True) & (frame['last_name_match'] == True), 'match'] = 'perfect match'
    frame.loc[(frame['first_name_match'] == False) & (frame['last_name_match'] == False), 'match'] = 'both names mismatch'
    
    #re-arrange column order
    frame = frame[['search_results_provided', 'social_used', 'eis_first_name', 'first_name', 'eis_last_name', 'last_name', 'match', 'ssid', 'ssn', 'dob', 'gender', 'ethnicity_race', 'tos', 'grade', 'eis_pin' ]]

    return(frame)

# -------------------------------send new data to Google Sheets------------------------------------

def send_new_data_to_sheets():
    # create spread instance, and send to SSID Lookip
    c = gspread_pandas.conf.get_config(conf_dir=os.getcwd(), file_name='google_secret.json')
    spread = Spread('SSID Lookup', config=c)

    # Get existing data if any for 23-24 New Data sheet
    existing_data = spread.sheet_to_df(sheet='23-24 New Data')

    # Concatenate the new data with the existing data
    concatenated_data = pd.concat([existing_data, frame], ignore_index=True)

    # Write the concatenated data back to the Google Sheet
    try:
        spread.df_to_sheet(concatenated_data, headers=True, replace=True, sheet='23-24 New Data', index=False, freeze_headers=True)
    except:
        print('Issue sending data to Google Sheet')

        
get_to_EIS_homepage()
frame, df = scrape_student_data()

if frame.empty == False:
    
    create_columns()
    frame = clean_frame_and_rearrange(frame)
    send_new_data_to_sheets()
    
    logging.info(f'\nNew data sent to sheets - {len(frame)} records')
    
else:
    logging.info('No new data to send')
    
# -------------------------------------------Begin Downloads---------------------------------------------------------------

def download_school_error_reports(school_full_xpath):
    
    window_handles = driver.window_handles
    driver.switch_to.window(window_handles[0])

    #click on EIS image
    span_element = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="orion-application"]/div[2]/tdoe-sidebar-layout/mat-sidenav-container/mat-sidenav-content/div/div[2]/article/app-orion-application-list/main/div/div/div[2]/app-orion-launch-card/mat-card/div'))
    )

    span_element.click()

    dropdown = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'mat-select-arrow-wrapper'))
    )
    dropdown.click()
    
    school_choice = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, school_full_xpath))
    )

    school_choice.click()


    launch_app = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@class="mat-focus-indicator mat-raised-button mat-button-base mat-primary"]/span[text()="Launch Application"]'))
    )

    # Click on the span element
    launch_app.click()
    
    #-------------------------------------app is launched now switch to other window and download report
    window_handles = driver.window_handles
    driver.switch_to.window(window_handles[-1])


    #Click on district_button
    district_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.NAME, 'district'))
    )
    district_button.click()

    #Click on submit button
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
    #download the file
    go_button.click()
    driver.close()
    
# ---------------------------------------------------------Get the ADM audits-------------------------------------

def get_adm_audit_student_membership(school_full_xpath):


    window_handles = driver.window_handles
    driver.switch_to.window(window_handles[0])


    #click on data reports image
    data_reports = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="orion-application"]/div[2]/tdoe-sidebar-layout/mat-sidenav-container/mat-sidenav-content/div/div[2]/article/app-orion-application-list/main/div/div/div[1]/app-orion-launch-card/mat-card/div'))
    )

    data_reports.click()


    dropdown = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'mat-select-arrow-wrapper'))
    )
    dropdown.click()


    school_choice = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, school_full_xpath))
    )

    school_choice.click()


    launch_app = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@class="mat-focus-indicator mat-raised-button mat-button-base mat-primary"]/span[text()="Launch Application"]'))
    )

    launch_app.click()

    #-------------------------------------app is launched now switch to other window and download report
    window_handles = driver.window_handles
    driver.switch_to.window(window_handles[-1])


    research_queries = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="NavigationMenu"]/ul/li[4]/a'))
    )

    research_queries.click()


    adm_audit = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, 'MainContent_HyperLink1'))
    )

    adm_audit.click()

    #could not get this dropdown to work without a brief sleep
    time.sleep(3)

    dropdown = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_MainContent_ReportViewer1_ctl05_ctl04_ctl00_Button"]'))
    )

    dropdown.click()


    file_download = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/form/div[3]/div[2]/span/div/table/tbody/tr[4]/td/div/div/div[4]/table/tbody/tr/td/div[2]/div[1]/a'))
    )

    file_download.click()
    
    #---------------------------------------
    
    driver.back()

    research_queries = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="NavigationMenu"]/ul/li[4]/a'))
    )

    research_queries.click()

    student_membership = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="MainContent_HyperLink19"]'))
    )

    student_membership.click()

    #could not get this dropdown to work without a brief sleep
    time.sleep(3)

    dropdown = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_MainContent_ReportViewer1_ctl05_ctl04_ctl00_Button"]'))
    )

    dropdown.click()


    file_download = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/form/div[3]/div[2]/span/div/table/tbody/tr[4]/td/div/div/div[4]/table/tbody/tr/td/div[2]/div[1]/a'))
    )

    file_download.click()

    driver.close()
    
    
# ---------------------------------------------Declaring Final Functions and recursive variables-------------------------------------------------
    
#full xpaths for dropdown selections    
school_dict =  {'WDL' : '/html/body/div[3]/div[4]/div/div/div/mat-option[1]/span',
                'KRB' : '/html/body/div[3]/div[4]/div/div/div/mat-option[2]/span',
                'HIL' : '/html/body/div[3]/div[4]/div/div/div/mat-option[3]/span',
                'BLF' : '/html/body/div[3]/div[4]/div/div/div/mat-option[4]/span',
                'FLY' : '/html/body/div[3]/div[4]/div/div/div/mat-option[5]/span'}

#clean out the directories before the new sends

adm_audit_path = 'P:\\Knowledge Management\\State Reporting\\TN\\EIS\\Exports\\EIS\\ADM Audit'
student_membership_path = 'P:\Knowledge Management\State Reporting\TN\EIS\Exports\EIS\Student Membership List'

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

    # move audit files over to proper directory

    for file in target_dir['files']:
        source_path = os.path.join(download_directory, file)
        destination_path = os.path.join(final_dest, file)

        shutil.move(source_path, destination_path)
        

#stack and send membership files      
def stack_membership_files_and_send():

    file_list = os.listdir(student_membership_path)

    # Initialize an empty list to hold DataFrames
    data_frames = []

    # Loop through the files and read them into DataFrames
    for file_name in file_list:
        if file_name.endswith('.csv'):  # Assuming your files are in CSV format
            file_path = os.path.join(student_membership_path, file_name)
            df = pd.read_csv(file_path, skiprows=3)
            data_frames.append(df)

    # Concatenate the DataFrames vertically
    stacked_df = pd.concat(data_frames, ignore_index=True)
    stacked_df['last_update'] = pd.Timestamp.today().date()

    #--------------------now send over-------------------
    
    quoted = urllib.parse.quote_plus("Driver={SQL Server Native Client 11.0};"
                     "Server=10.0.0.89;"
                     "Database=DataTeamSandbox;"
                     "Trusted_Connection=yes;")

    engine = sqlalchemy.create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))

    # specify data types for VARCHARs because the length defaults to max.  
    stacked_df.to_sql('TN_Student_Membership', schema='dbo', con = engine, if_exists = 'replace', index = False)

    engine.dispose()
    
    
# ---------------------------Calling the process---------------------------------------

clean_dir(download_directory)
clean_dir(adm_audit_path)
clean_dir(student_membership_path)
logging.info(f'Directories cleaned')


for xpath in school_dict.values():
    download_school_error_reports(xpath)
logging.info(f'School error reports downloaded')
    
for xpath in school_dict.values():
    get_adm_audit_student_membership(xpath)
logging.info(f'ADM audit and student reports downloaded')
    
#Must call sleep to give the final download time to get in the directory
time.sleep(15)
move_files('audit', adm_audit_path)
move_files('membership', student_membership_path)
logging.info(f'Files moved to proper dirs')

stack_membership_files_and_send()
logging.info(f'Membership data sent to 89\n\n--------------------------------')
driver.quit()

