import os
import logging
import shutil
import time
import pandas as pd
from .selenium_process import get_adm_audit_student_membership

def clear_logging_handlers():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

def make_dir(dir):
    try:
        os.makedirs(dir, exist_ok=True)
        logging.info(f'Directory "{dir}" created or already exists.')
        print(f'Directory "{dir}" created or already exists.')
    except Exception as e:
        print(f'An error occurred while creating the directory: {e}')
        logging.info(f'An error occurred while creating the directory: {e}')


def clean_dir(dir_path):
    if os.path.exists(dir_path):
        logging.info(f'Cleaning out dir "{dir_path}"')
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            else:
                pass


def wait_for_cr_files(directory, sleep_time=10):

    time.sleep(sleep_time)

    while True:
        # Get list of all files in the directory
        files = os.listdir(directory)
        
         # Check if any file has a .cr or .tmp extension
        temp_files = [file for file in files if file.endswith('.crdownload') or file.endswith('.tmp')]
        
        if not temp_files:
            print("No .crdownload or .tmp files found. Proceeding...")
            logging.info("No .crdownload or .tmp files found. Proceeding...")
            break
        
        print(f".crdownload or .tmp files found: {temp_files}. Sleeping for {sleep_time} seconds...")
        logging.info(f".crdownload or .tmp files found: {temp_files}. Sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)




def copy_directory(source_dir, dest_dir):
    # Ensure the destination directory exists
    os.makedirs(dest_dir, exist_ok=True)
    try:
        # Copy the source directory to the destination directory
        shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
        logging.warning(f'{source_dir} copied to {dest_dir}')
    except Exception as e:
        logging.warning('Unable to move {source_dir} to {dest_dir} due to \n {e}')




def send_to_SFTP(download_dir, sftp_path, str_match):
    # Find all files in the download directory that match the str_match pattern
    matching_files = [os.path.join(download_dir, f) for f in os.listdir(download_dir) if str_match in f and f.endswith('.csv')]

    if not matching_files:
        logging.error(f'No files found in {download_dir} matching {str_match}')
        return

    # Initialize an empty list to hold DataFrames
    dataframes = []

    # Read each matching file into a DataFrame and append to the list
    for file in matching_files:
        try:
            df = pd.read_csv(file, header=2)
            dataframes.append(df)
            logging.info(f'Read file {file} successfully')
        except Exception as e:
            logging.error(f'Error reading file {file}: {str(e)}')

    # Concatenate all DataFrames into a single DataFrame
    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
    else:
        logging.error(f'No valid dataframes to concatenate for {str_match}')
        return

    # Construct the output file path
    end_str = f'{str_match}_stack.csv'
    output_path = os.path.join(sftp_path, end_str)

    try:
        # Save the combined DataFrame to the specified output path
        combined_df.to_csv(output_path, index=False)
        logging.info(f'Sending {str_match} csv to {output_path}')
    except Exception as e:
        logging.error(f'Unable to send stacked csv to {output_path} due to error: \n {e}')




# school_dict_1 =  {'ASD': ' District User (Achievement School District) ',
#                 'BLF' : ' School User (Bluff City High School - Tennessee Public Charter School Commission) '
#                 }
                #   'ACH': ' SCH (ASD ESA School - Achievement School District) ' }
                    # 'HIL' : ' School User (Hillcrest High School - Achievement School District) '
                    # 'WDL' : ' School User (Wooddale Middle School - Achievement School District) ',
                    # 'KRB' : ' School User (Kirby Middle School - Achievement School District) ',
                    # 'FLY' : ' School User (Fairley High School - Achievement School District) '}



# school_dict_2 =  {'ASD': 'Not sure what this path is supposed to be yet',
#                  'BLF' : ' SCH_EC (Bluff City High School - Tennessee Public Charter School Commission) '
#                  }
                 #old one is the charter school comission
                #   'ACH': ' SCH_EC (ASD ESA School - Achievement School District) '}
                    # 'HIL' : ' SCH (Hillcrest High School - Achievement School District) '}
                    # 'WDL' : ' SCH (Wooddale Middle School - Achievement School District) ',
                    # 'KRB' : ' SCH (Kirby Middle School - Achievement School District) ',
                    # 'FLY' : ' SCH (Fairley High School - Achievement School District) '}

# <mat-option _ngcontent-fwe-c135="" role="option" class="mat-option mat-focus-indicator ng-tns-c124-19 ng-star-inserted" id="mat-option-12" tabindex="0" aria-disabled="false" style=""><!----><span class="mat-option-text"> SCH_EC (ASD ESA School - Achievement School District) </span><div mat-ripple="" class="mat-ripple mat-option-ripple"></div></mat-option>


# combined_dict = list(zip(school_dict_1.items(), school_dict_2.items()))


def get_adm_audit_student_membership_loop(driver, which_school):

    school_dict_1 =  {'ASD': ' District User (Achievement School District) ',
                    'BLF' : ' School User (Bluff City High School - Tennessee Public Charter School Commission) '
                    }

    school_dict_2 =  {'ASD': 'Not sure what this path is supposed to be yet',
                        'BLF' : ' SCH_EC (Bluff City High School - Tennessee Public Charter School Commission) '
                        }
    combined_dict = list(zip(school_dict_1.items(), school_dict_2.items()))

    combined_dict = [item for item in combined_dict if item[0][0] == which_school]

    logging.info(f'Here is the combined dict {combined_dict}')


    try:
        logging.info('Calling get_adm_audit_student_membership')
     
        for (schools1, xpaths1), (schools2, xpaths2) in combined_dict:
            logging.info(f'Processing schools1: {schools1}, passing in both xpaths to func get_adm_audit_student_membership')
            get_adm_audit_student_membership(driver, xpaths1, xpaths2, schools1)

    except Exception as e:
        logging.info(f'Error due to {e}')

    