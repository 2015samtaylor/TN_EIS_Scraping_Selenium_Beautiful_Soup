import logging
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException, ElementClickInterceptedException, WebDriverException

# -------------------------------------------------------------------------------
# If it is a 500 error, there is no solution



def get_to_EIS_homepage_with_retry(username, password, driver, url, max_retries=4 ):
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

            try:
                # Click on the link
                login_link.click()
                logging.info('Clicked login link')
            except:
                logging.info('Unable to click login link')

            # Wait for login box to appear, and send username
            username_input = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.NAME, 'loginfmt'))
            )
            try:
                username_input.send_keys(username)
                logging.info('Username sent')
            except:
                logging.info('Unable to send username')

            submit = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, 'idSIButton9'))
            )

            try:
                submit.click()
                logging.info(f'Submitted username as {username}')
            except:
                logging.info('Unable to submit username')


            # Wait for password input to appear, and send password
            password_input = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.NAME, 'passwd'))
            )
            try:
                password_input.send_keys(password)
                logging.info(f'Sent password as {password}')
            except:
                logging.info("Unable to send password")

            submit = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, 'idSIButton9'))
            )

            try:
                submit.click()
                logging.info('Submitted username and password')
            except:
                logging.info('Unable to submit username and password')


            # If we've reached this point without exceptions, the function has succeeded, can exit the while loop
            return('Success')

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Retrying...")
            logging.info(f'An error occured: {e} retrying')
            retries += 1
            time.sleep(3)  # Add a delay before retrying

    print(f"Max retries reached ({max_retries}). Function failed.")
    logging.info(f'Max retries reached ({max_retries}). Function failed')
    

# -------------------------------------------Begin Downloads---------------------------------------------------------------
data_reports_image = f"//img[@src='{'/assets/img/applications/EISREPORTING.gif'}']"
eis_image = f"//img[@src='{'/assets/img/applications/EISPROD.gif'}']"


def open_app_select_school(xpaths1, xpaths2, schools1, app_xpath, driver):

    try:
        image_element = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "img.tdoe-branding"))
        )
        logging.info('Image element has been located. Application page loaded in 60 secs')
    except:
        logging.info('The application page is failing to load in 60 secs')

    
    window_handles = driver.window_handles
    try:
        driver.switch_to.window(window_handles[0])
        logging.info('Switched driver windows')
    except Exception as e:
        logging.info('Unable to switch driver windows due to {e}')

    #click on image
    span_element = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, app_xpath))
    )

    try:
        span_element.click()
        logging.info(f'Clicked on {app_xpath}')
    except:
        logging.info(f'Unable to click on {app_xpath}')

    dropdown = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'mat-select-arrow-wrapper'))
    )
    try:
        dropdown.click()
        logging.info('Clicked on dropdown')
    except:
        logging.info('Unable to click on dropdown')

    first_xpath_success = None
    
    try:
        
        school_choice = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//span[@class="mat-option-text" and text()="{}"]'.format(xpaths1)))
        )
        logging.info(f"school_choice element {schools1} found and clickable through {xpaths1}.")
        school_choice.click()

        first_xpath_success = True

    except Exception as e:
        logging.info(f'Exception caught. school_choice element unable to be clicked upon due to {e}')
        logging.info(f"First xpath did not work for school - {schools1}")
        logging.info(f'Trying this xpath {xpaths2}')

        first_xpath_success=False

    if first_xpath_success == False: 

        try:
            school_choice = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@class="mat-option-text" and text()="{}"]'.format(xpaths2)))
            )
            school_choice.click()
            logging.info(f"school_choice element {schools1} found and clickable through {xpaths1}.")

        except Exception as e:
            logging.info(f"Second xpath did not work for school - {schools1}")
            
# -------------------------------------------------------------------------------------
def launch_application(xpaths1, xpaths2, schools1, app_choice, driver, max_retries=4, retry_delay=5):

    for retry in range(max_retries):
        try:
            launch_app = driver.find_element(By.XPATH, "//span[contains(text(),'Launch Application')]")

            try:
                # Click on the span element
                launch_app.click()
            except Exception as e:
                logging.error(f'Unable to launch application due to {e}')

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
                logging.info('app variable is wrong')
            

            # If the launch was successful, break out of the retry loop
            break

        except (TimeoutException, NoSuchElementException, NoSuchWindowException, AttributeError) as e:
            logging.info(f'Issue launching app for {schools1}')
            if retry < max_retries - 1:
                # recreate conn with window
                window_handles = driver.window_handles
                driver.switch_to.window(window_handles[0])

                # Navigating back to a previous page
                driver.back()
                
                #The xpaths should be good here as the switching happesn within the func 
                open_app_select_school(xpaths1, xpaths2, schools1, eis_image, driver)

                # Wait before retrying
                time.sleep(retry_delay)
            else:
                logging.info(f'Max retries reached for {schools1}. Giving up.')

                
# -----------------------Download School Error Reports-----------------------------------



def download_school_error_reports(xpaths1, schools1, xpaths2, driver):

    try:
        open_app_select_school(xpaths1, xpaths2, schools1, eis_image, driver)
    except Exception as e:
        logging.error(f"Failed to select school {schools1} due to: {e}")
        return  # Exit if school selection fails
    
    try:
        launch_application(xpaths1, xpaths2, schools1, 'EIS', driver, max_retries=4, retry_delay=5)
    except Exception as e:
        logging.error(f"Failed to launch application for {schools1} due to: {e}")
        return  # Exit if application launch fails
  
    #-----------------In district tab, now submitting form and downloading the file------------------------
    
    submit_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.NAME, 'SUBMIT'))
    )
    try:
        submit_button.click()
        logging.info('Clicked on submit')
    except:
        logging.info('Unable to click on submit button')

    #click on dynamic errors button
    dynamic_errors = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.LINK_TEXT, 'Dynamic Errors'))
    )
    try:
        dynamic_errors.click()
        logging.info('Clicked on dynamic errors')
    except:
        logging.info('Unable to click on dynamic errors')

    go_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/table[3]/tbody/tr/td[2]/table/tbody/tr/td/form/table/tbody/tr/td[2]/a/img'))
    )
    try:
        go_button.click()
        logging.info('Clicked on go button')
    except:
        logging.info('Unable to click on go button')

    # ----------------------------------------------------

    dropdown = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.NAME, 'locat'))
    )
    try:
        dropdown.click()
        logging.info('Clicked on dropdown')
    except:
        logging.info('Unable to click on dropdown')

    School_Level_Errors = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/table[3]/tbody/tr/td[2]/table/tbody/tr/td/form/table/tbody/tr/td[2]/select/option[2]'))
    )
    try:
        School_Level_Errors.click()
        logging.info('Unable to click on School Level Errors')
    except:
        logging.info('Clicked on school level errors')


    go_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/table[3]/tbody/tr/td[2]/table/tbody/tr/td/form/table/tbody/tr/td[2]/a/img'))
    )

    try:
        go_button.click()
        logging.info('Clicked on go button')
    except:
        logging.info('Unable to click on go button')


    # in next window now

    dropdown = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.NAME, 'select2'))
    )
    try:
        dropdown.click()
        logging.info('Clicked on dropdown')
    except:
        logging.info('Unable to click on dropdown')



    Download_All_School_Errors = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/table[3]/tbody/tr/td[2]/table/tbody/tr/td/form/table/tbody/tr[2]/td[3]/select/option[2]'))
    )
    try:
        Download_All_School_Errors.click()
        logging.info('Clicked on download all school errors')
    except:
        logging.info('Unable to click on download all school errors')


    #Got hung up HERE
    go_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/table[3]/tbody/tr/td[2]/table/tbody/tr/td/form/table/tbody/tr[2]/td[3]/a/img'))
    )
    
    try:
        #download the file
        go_button.click()
        driver.close()   
        logging.warning(f'Downloaded {schools1} school error reports')
        
    except Exception as e:
        logging.warning(f'Failed to download {schools1} school error reports')
            
    




# ------------------Unique to EIS_adm_audit_membership--------------------
# ------------------------div style changed has to do with dropdown loading before clicking on it---------------
                
def div_style_changed(driver):


    div_locator = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_ReportViewer1_AsyncWait')))

    style_attribute = div_locator.get_attribute("style")

    output = style_attribute.split(";")[3].strip().split(':')[1].strip()

    return(output == 'none')         


    
                


def get_adm_audit_student_membership(driver, xpaths1, xpaths2, schools1):   

    logging.info('Moving to open_app_select_schools function')

    #I think this piece gets hit too fast
    open_app_select_school(xpaths1, xpaths2, schools1, data_reports_image, driver)
    launch_application(xpaths1, xpaths2, schools1, 'Data_Reports', driver, max_retries=4, retry_delay=5)
    
    #

    adm_audit = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, 'MainContent_HyperLink1'))
    )
    try:
        adm_audit.click()
        logging.info('ADM audit clicked')
    except:
        logging.info('Unable to click on adm audit')

    #could not get this dropdown to work without a brief sleep
    time.sleep(3)

    dropdown = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, "//img[@alt='Export drop down menu']"))
    )
    try:
        dropdown.click()
        logging.info('Clicked on dropdown')
    except:
        logging.info('Unable to click on dropdown')

    file_download = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, "//a[@alt='CSV (comma delimited)']"))
   )
    
    try:
        file_download.click()
        logging.info(f'Downloaded {schools1} adm audit')
        
    except Exception as e:
        logging.info(f'Failed to download {schools1} adm audit')
        
    time.sleep(3)
    
    
    #---------------------------------------get student membership------------------------------
    
    driver.back()

    research_queries = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="NavigationMenu"]/ul/li[4]/a'))
    )
    try:
        research_queries.click()
        logging.info('Clicked on research queries')
    except:
        logging.info('Unable to click on research queries')

    student_membership = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="MainContent_HyperLink19"]'))
    )
    try:
        student_membership.click()
        logging.info('Student Membership clicked')
    except:
        logging.info('Unable to click on student membership')
    
    loaded = WebDriverWait(driver, 30).until(lambda d: div_style_changed(d))

    if loaded == True:
        logging.info('variable loaded')
    else:
        time.sleep(3)
        logging.info('Issue with the variable loading on the dropdown')
    
    
    dropdown = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, "//img[@alt='Export drop down menu']"))
    )
    try:
        dropdown.click()
        logging.info('Dropdown clicked')
    except:
        logging.info('Issue with the dropdown not loading fast enough')

    file_download = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, "//a[@alt='CSV (comma delimited)']"))
    )
    
    try:
        file_download.click()
        logging.info(f'Downloaded {schools1} student membership')
        
    except Exception as e:
        logging.info(f'Failed to download {schools1} student membership')
        
    driver.close()
    
