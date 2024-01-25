#!/usr/bin/env python
# coding: utf-8


# In[6]:

#currently a manual trigger at the beginning of the year, when new students are incoming

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException
from bs4 import BeautifulSoup
import pandas as pd
from gspread_pandas import Spread, Client
import gspread_pandas
import os
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
password = 'll!MIPxP03'

# -----------------------------------------------------

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

         #click on EIS production image
        span_element = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="orion-application"]/div[2]/tdoe-sidebar-layout/mat-sidenav-container/mat-sidenav-content/div/div[2]/article/app-orion-application-list/main/div/div/div[2]/app-orion-launch-card/mat-card/div'))
        )


        span_element.click()
        

        launch_app = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@class="mat-focus-indicator mat-raised-button mat-button-base mat-primary"]/span[text()="Launch Application"]'))
        )

        # Click on the span element
        launch_app.click()
        
        #---------------------
        
        # Get the list of window handles
        window_handles = driver.window_handles

        # # Switch to the new window
        new_window_handle = window_handles[-1]
        driver.switch_to.window(new_window_handle)

        student_lookup = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/table[3]/tbody/tr/td[1]/table/tbody/tr[5]/td/a'))
        )
        student_lookup.click()
        

    except (TimeoutException, NoSuchElementException, NoSuchWindowException, AttributeError) as e:
        
        #recreate conn with window
        window_handles = driver.window_handles
        driver.switch_to.window(window_handles[0])
        
        # Navigating back to a previous page or taking another appropriate action
        driver.back()
        
        #click on EIS production image
        span_element = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="orion-application"]/div[2]/tdoe-sidebar-layout/mat-sidenav-container/mat-sidenav-content/div/div[2]/article/app-orion-application-list/main/div/div/div[2]/app-orion-launch-card/mat-card/div'))
        )

        span_element.click()
        

        launch_app = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@class="mat-focus-indicator mat-raised-button mat-button-base mat-primary"]/span[text()="Launch Application"]'))
        )

        # Click on the span element
        launch_app.click()
        
        # Get the list of window handles
        window_handles = driver.window_handles

        # # Switch to the new window
        new_window_handle = window_handles[-1]
        driver.switch_to.window(new_window_handle)

        student_lookup = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/table[3]/tbody/tr/td[1]/table/tbody/tr[5]/td/a'))
        )
        student_lookup.click()
        
# -------------------------------Student Lookup Window is launched, now scrape student data--------------------------------
        
def scrape_student_data():
    
    # For loop starts here. 
    # read in frame, and get students that are not done yet. 
    
    c = gspread_pandas.conf.get_config(conf_dir=os.getcwd(), file_name='google_secret.json')
    spread = Spread('SSID Lookup', config=c)

    # Read data from an Excel sheet
    df = spread.sheet_to_df(index = 1, sheet='23-24')   
    
    #TEMPORARY TESTING 
#     df = df.iloc[:10]
    
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
    
    print(df_list)
    
    try:
    
        frame = pd.DataFrame(df_list, columns= column_names)
    
    #If there is only one record and comes back empty, error with inserting into columns
    except:
        
        # Create a DataFrame with empty values
        frame = pd.DataFrame(columns=column_names)

        frame.loc[0, 'eis_name'] = df_list[0][0]

    # Define the regular expression pattern
    pattern = r'(.*?)(n/a|x{1,})(\d*)'

    # Extract the desired values from the column
    frame['ssn'] = frame['ssn'].str.extract(pattern)[0]
    frame['eis_pin'] = frame['ssn'].str.extract(pattern)[2]

    return(frame, df)

# -----------------------------------Functions to clean & re-arrange dataframe prior to Google Sheet send-------------------

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

# ---------------------------Calling the process---------------------------------------

get_to_EIS_homepage()
frame, df = scrape_student_data()

# If there is data, cleanse the frame, rearrange, and send the data to Google Sheets, otherwise log out the pass
if frame.empty == False:
    
    create_columns()
    frame = clean_frame_and_rearrange(frame)
    send_new_data_to_sheets()
    
    logging.info(f'\nNew data sent to sheets - {len(frame)} records')
    print(f'\nNew data sent to sheets - {len(frame)} records')
    
else:
    logging.info('No new data to send')
    print('No new data to send')

