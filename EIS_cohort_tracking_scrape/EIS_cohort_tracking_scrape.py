import pyodbc
import pandas as pd
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
import logging
import re
import numpy as np
import sqlalchemy
import pyodbc
from sqlalchemy import create_engine
import urllib
from sqlalchemy import create_engine, VARCHAR,Float, Integer

logging.basicConfig(filename='EIS_enrollment_scrape.log', level=logging.INFO,
                   format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',force=True)


# Specify the download directory
download_directory = r"P:\Knowledge Management\State Reporting\TN\EIS\Exports\EIS\EIS File Errors"  

# Set up Chrome options
chrome_options = webdriver.ChromeOptions()
prefs = {'download.default_directory' : download_directory,
         'profile.default_content_setting_values.automatic_downloads': 1,
         'profile.content_settings.exceptions.automatic_downloads.*.setting': 1}
chrome_options.add_experimental_option('prefs', prefs)

chrome_service = Service(r'C:\Users\samuel.taylor\Desktop\Python_Scripts\EIS\ChromeDriver\chromedriver.exe')
driver = webdriver.Chrome(ChromeDriverManager().install(), options = chrome_options)
url = 'https://orion.tneducation.net/unauthorized'

username = 'eduardo.ruedas@tneducation.net'
password = 'll!MIPxP03'

# -------------------------------Get Student Data to pass into the EIS---------------------------------------

def SQL_query(query):
    odbc_name = 'GD_DW'
    conn = pyodbc.connect(f'DSN={odbc_name};')
    df_SQL = pd.read_sql_query(query, con = conn)
    return(df_SQL)
    
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

# ------------------------------------Define the Scrape--------------------------------------------
    
def scrape_student_data(df):
    #for testing purposes
    # df = df.iloc[200:400]
    
    df.rename(columns = {'First_Name': 'first_name', 'Last_Name': 'last_name', 'SSN': 'ssn', 'DOB': 'dob'}, inplace = True)
    # df['dob'] = df['dob'].apply(lambda x: x.strftime("%m/%d/%Y"))
    df['dob'] = df['dob'].apply(lambda x: x.strftime("%m/%d/%Y") if x is not None else None)
    

    #cleaning
    df['first_name'] = df['first_name'].fillna('')
    df['last_name'] = df['last_name'].fillna('')
    df['ssn'] = df['ssn'].replace('', 0)
    
    #make sure ssn it a float so it can be recognized by if statement
    df['ssn'] = pd.to_numeric(df['ssn'], errors='coerce')
    df['ssn'] = df['ssn'].replace(0.0, np.NaN)
    df['ssn'] = df['ssn'].astype(float)
    

    student_data = []

    for index, row in df.iterrows():
        print(index)
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
        if not pd.isna(ssn) and ssn != 0.0:

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
        
        #now scrape the webpage
                # ------------------------Beautiful Soup Portion, scraping the HTML for proper data, append to data_list-----------

        # Step 3: Use Selenium to get the page source
        page_source = driver.page_source

        # Step 4: Use BeautifulSoup to parse the page source and extract the data
        soup = BeautifulSoup(page_source, 'html.parser')


        # Identify the tr tags, by their unique quality bgcolor
        parent_element = soup.find_all("tr", bgcolor={"#FAFAD2", "#FFFFFF"})  # Replace with a relevant selector
        

        for row in parent_element:
            try:
                columns = row.find_all('td')

                # Extract data from columns
                name = columns[0].text.strip()
                student_id = columns[1].text.strip()
                ssn_pin = columns[2].text.strip()
                date_of_birth = columns[3].text.strip()
                gender = columns[4].text.strip()
                ethnicity_race = columns[5].text.strip()
                TOS = columns[6].text.strip()
                grade = columns[7].text.strip()

                #special cases

                enrollment_dates = columns[9].text.strip()
                matches = re.split(r'([A-Za-z])', enrollment_dates, maxsplit=1)

                if len(matches) == 3:
                    enrollment = matches[0] + matches[1] 
                    withdraw = matches[2]  
                else:
                    print("Unexpected format with enrollment withdraw.")



                #school_info is a special case, get the raw html tag and then dive further into the nobr in order to split
                school_info = columns[8]

                # Find all <nobr> elements within the <td> element
                nobr_elements = school_info.find_all('nobr')

                # Extract the text from the <nobr> elements
                if len(nobr_elements) >= 2:
                    district = nobr_elements[0].get_text()
                    school = nobr_elements[1].get_text()
                else:
                    district = ''
                    school = ''


                # Create a dictionary to store the student data
                student_info = {
                    "Name": name,
                    "State ID": student_id,
                    'SSN PIN': ssn_pin,
                    "Date of Birth": date_of_birth,
                    'Gender': gender,
                    "Ethnicity Race": ethnicity_race,
                    'TOS': TOS,
                    "Grade": grade,
                    "District": district,
                    'School': school,
                    "Enrollment": enrollment,
                    'Withdraw': withdraw
                    # Add more fields as needed
                }



            except:
                print(f_name + ' ' + l_name + '' + dob)
                student_info = {
                    "Name": f_name + ' ' + l_name,
                    "State ID": '',
                    'SSN PIN': ssn,
                    "Date of Birth": dob,
                    'Gender': '',
                    "Ethnicity Race": '',
                    'TOS': '',
                    "Grade": '',
                    "District": '',
                    'School': '',
                    "Enrollment": '',
                    'Withdraw': ''
            }
    
            student_data.append(student_info)
        driver.back()
          
    #return the student data outside of each for loop
    return(student_data)

# -----------------------------------------Functions to clean up the HTML--------------------------------

# Function to cleanse frame of '\xa0'
def replace_non_breaking_space(text):
    return re.sub(r'\xa0', ' ', text)

def clean_up(frame):
    split_columns = frame['Name'].str.split(',', expand = True)

    # Rename the new columns as needed
    split_columns.rename(columns={0: 'eis_last_name', 1: 'eis_first_name', 2: 'eis_middle_name', 3: 'eis_other'}, inplace=True)
    split_columns = split_columns[['eis_last_name', 'eis_first_name']]

    frame = pd.concat([frame, split_columns], axis=1)
    frame = frame.drop(columns = ['Name'])

    # Define a regular expression pattern to match SSNs
    ssn_pattern = re.compile(r'\d{3}-?\d{2}-?\d{4}')

    # Split out SSN, and EIS pin then drop original column
    frame['EIS PIN'] = frame['SSN PIN'].apply(lambda s: ssn_pattern.search(s).group() if ssn_pattern.search(s) else None)
    frame['SSN'] = frame['SSN PIN'].apply(lambda s: ssn_pattern.sub('', s).strip() if ssn_pattern.search(s) else s)
    frame['SSN'] = frame['SSN'].str.replace('n/a', '')  
    frame = frame.drop(columns = ['SSN PIN'])  
    
    # Break apart ethnicity race, and concat back to the frame
    sub = frame['Ethnicity Race'].str.replace('\t', '').str.split(expand = True)
    sub.rename(columns = {0: 'Ethnicity', 1: 'Race'}, inplace  = True)
    frame = pd.concat([frame, sub], axis=1)
    frame = frame.drop(columns = ['Ethnicity Race'])
    
    
    # Replace the 'n/a'
    #Change the 'R' to transfers
    #Fix one off
    frame["Withdraw"] = frame['Withdraw'].str.replace(r'\s*n/a\s*', '', regex=True)
    frame['Withdraw'] = frame['Withdraw'].str.replace('R', '')
    frame['Withdraw'] = frame['Withdraw'].str.replace('/a', '')
    frame['Enrollment'] = frame['Enrollment'].str.replace(r'T$', 'TR', regex=True)
    frame["Enrollment"] = frame["Enrollment"].str.replace('- n', '')
    
    frame = frame[['eis_first_name', 'eis_last_name', 'State ID', 'SSN', 'EIS PIN', 'Date of Birth', 'Gender', 'TOS', 'Grade', 'District', 'School', 'Enrollment', 'Withdraw']]

    return(frame)

# --------------------------Query for existing records, find out what is new, append to log_results.csv---------------------

def SQL_query_89(query):
    odbc_name = 'GD_DW_89'
    conn = pyodbc.connect(f'DSN={odbc_name};')
    df_SQL = pd.read_sql_query(query, con = conn)
    return(df_SQL)


def get_new_records(frame, current_db_records):
    # Combine the two DataFrames into one
    combined_df = pd.concat([frame, current_db_records], ignore_index=True)

    # Identify the duplicates (existing records)
    duplicates = combined_df[combined_df.duplicated(keep='first')]

    # Find the new records by excluding the duplicates from df2
    new_records = current_db_records[~current_db_records.isin(duplicates)].dropna()

    #Fix the SSN 
    new_records['SSN'] = new_records['SSN'].str.replace(r'^n/a', '', regex=True)

    return(new_records)


# ------------------------------------------------------------------------------------
# These log_results are based on last update

def append_log_results():

    file = os.getcwd() + '\\new_student_records.csv'

    # Check if the file exists before writing
    if not os.path.exists(file):
        
        new_records.to_csv(file, index=False)

    else:

        # Read the master frame
        df_source = pd.read_csv(file)

        # Append the new log_results to the original
        updated = pd.concat([df_source, log_results], ignore_index=True)
        
        updated = updated.drop_duplicates()

        # Write the updated destination DataFrame back to the CSV file
        updated.to_csv('log_results.csv', index=False)
        

# --------------------------Calling the process------------------------------------------
            
get_to_EIS_homepage()

query = SQL_query(
'''
SELECT First_Name, Last_Name, SSN, DOB, Gender, SchoolEntryDate
FROM [PowerschoolStaged].[dbo].[vw_Rpt_TennStudents]
WHERE SchoolEntryDate > '2020/08/01'
ORDER BY SchoolEntryDate DESC
''')
            
student_data = scrape_student_data(query)

frame = pd.DataFrame(student_data)

frame = frame.applymap(replace_non_breaking_space)
frame = clean_up(frame)

frame.to_csv('Entire_Scrape.csv', index =False)
#Took out piece that only brings in new rows, issue last time was with data types not matching. 
# current_db_records = SQL_query_89('SELECT * FROM [DataTeamSandbox].[dbo].[EIS_enrollment_history]')
# new_records = get_new_records(frame, current_db_records)

# ------------------------------------------------------------------create pyodbc engine to send data to sandbox------

quoted = urllib.parse.quote_plus("Driver={SQL Server Native Client 11.0};"
                     "Server=10.0.0.89;"
                     "Database=DataTeamSandbox;"
                     "Trusted_Connection=yes;")

engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))

dtype_dict = {
    'eis_first_name':  VARCHAR(length=75),
    'eis_last_name':  VARCHAR(length=75),
    'State ID': Integer(),
    'SSN': VARCHAR(length=75),
    'EIS PIN': VARCHAR(length=75),
    'Date of Birth': VARCHAR(length=75),
    'Gender': VARCHAR(length=75),
    'TOS': VARCHAR(length=75),
    'Grade': VARCHAR(length=75),
    'District': VARCHAR(length=75),
    'School': VARCHAR(length=75),
    'Enrollment': VARCHAR(length=75),
    'Withdraw': VARCHAR(length=75)
}

try:
    frame.to_sql('EIS_enrollment_history' , schema='dbo', con = engine, if_exists = 'replace', index = False, dtype = dtype_dict)
    logging.info('New records succesfully sent to EIS_enrollment_history, and new students appended to new_student_records.csv\n\n')
    # append_log_results()
except Exception as e:
    logging.info('New students were UNABLE to send, error when trying to send as {e}\n\n')