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




def stack_files(dir, str_match):   #needs to include string matching.

    all_frames = []

    print(dir, str_match)

    for file in os.listdir(dir):
        if str_match in file:

            logging.warning(f'Stacking {file} based on string match {str_match}')
            print(f'Stacking {file} based on string match {str_match}')

            file_path = os.path.join(dir, file)
    
            if str_match == 'AllErr':  #Subject to change
                df  = pd.read_csv(file_path, usecols=list(range(32))) #Must read in 32 columns, because the file adds in commas for any errors at the end of the file
            elif str_match == 'ADMAudit':
                df  = pd.read_csv(file_path, header=2)
            elif str_match == 'StudentMembership':
                df  = pd.read_csv(file_path, header=2)

            all_frames.append(df)
        
        else:
            logging.debug(f'Str match of {str_match} passed upon for file {file} in stacking files')


    df = pd.concat(all_frames)
    df = df.dropna(how='all')
    today = pd.Timestamp.today().normalize()
    df['Last_Update'] = today

    logging.info(f'{str_match} being sent over with {df['SCHOOL_NO'].unique()} schools')
    return(df)





def stack_files_send_to_SFTP(dir, sftp_path, str_match):

    df = stack_files(dir, str_match)

    # Construct the output file path
    end_str = f'{str_match}_stack.csv'
  
    output_path = os.path.join(sftp_path, end_str)

    try:
        # Save the DataFrame to the specified output path
        df.to_csv(output_path, index=False)
        logging.warning(f'Sending stacked csv to {output_path}')
    except Exception as e:
        logging.warning(f'Unable to send stacked csv to {output_path} due to error: \n {e}')




school_dict_1 =  {'BLF' : ' School User (Bluff City High School - Tennessee Public Charter School Commission) ',
                    'HIL' : ' School User (Hillcrest High School - Achievement School District) '}
                    # 'WDL' : ' School User (Wooddale Middle School - Achievement School District) ',
                    # 'KRB' : ' School User (Kirby Middle School - Achievement School District) ',
                    # 'FLY' : ' School User (Fairley High School - Achievement School District) '}


school_dict_2 =  {'BLF' : ' SCH_EC (Bluff City High School - Tennessee Public Charter School Commission) ', #old one is the charter school comission
                    'HIL' : ' SCH (Hillcrest High School - Achievement School District) '}
                    # 'WDL' : ' SCH (Wooddale Middle School - Achievement School District) ',
                    # 'KRB' : ' SCH (Kirby Middle School - Achievement School District) ',
                    # 'HIL' : ' SCH (Hillcrest High School - Achievement School District) ',
                    # 'FLY' : ' SCH (Fairley High School - Achievement School District) '}


combined_dict = list(zip(school_dict_1.items(), school_dict_2.items()))


def get_adm_audit_student_membership_loop(driver):
    try:
        if not combined_dict:
            logging.error('combined_dict_list is empty or not defined correctly')
        else:
            logging.info('Calling get_adm_audit_student_membership')
            for (schools1, xpaths1), (schools2, xpaths2) in combined_dict:
                logging.info(f'Processing schools1: {schools1}, passing in both xpaths to func get_adm_audit_student_membership')
                get_adm_audit_student_membership(driver, xpaths1, xpaths2, schools1)
    except Exception as e:
        logging.info(f'Error due to {e}')

    