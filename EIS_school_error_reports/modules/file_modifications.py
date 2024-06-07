import os
import logging
import shutil
import time
import pandas as pd

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

    while True:
        # Get list of all files in the directory
        files = os.listdir(directory)
        
         # Check if any file has a .cr or .tmp extension
        temp_files = [file for file in files if file.endswith('.crdownload') or file.endswith('.tmp')]
        
        if not temp_files:
            print("No .crdownload or .tmp files found. Proceeding...")
            break
        
        print(f".crdownload or .tmp files found: {temp_files}. Sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)




def copy_directory(source_dir, dest_dir):
    # Ensure the destination directory exists
    os.makedirs(dest_dir, exist_ok=True)
    try:
        # Copy the source directory to the destination directory
        shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
        logging.info(f'{source_dir} copied to {dest_dir}')
    except Exception as e:
        logging.info('Unable to move {source_dir} to {dest_dir} due to \n {e}')







def stack_files_send_to_SFTP(dir, sftp_path):

    all_frames = []

    for file in os.listdir(dir):
        file_path = os.path.join(dir, file)
        logging.info(f'Stacking {file}')
        print(f'Stacking {file}')

        columns_to_read = list(range(32)) #Must read in 32 columns, because the file adds in commas for any errors at the end of the file
        df  = pd.read_csv(file_path, usecols=columns_to_read)
        all_frames.append(df)

    df = pd.concat(all_frames)
    df = df.dropna(how='all')
    today = pd.Timestamp.today().normalize()
    df['Last_Update'] = today

    num_of_schools = len(df['SCHOOL_NAME'].unique())
    logging.info(f'{num_of_schools} have been stacked')
    print(f'{num_of_schools} files have been stacked')

    end_str = 'School_Error_Reports_stack.csv'

    # Construct the output file path
    output_path = os.path.join(sftp_path, end_str)

    try:
        # Save the DataFrame to the specified output path
        df.to_csv(output_path, index=False)
        logging.info(f'Sending stacked csv to {output_path}')
    except Exception as e:
        logging.info(f'Unable to send stacked csv to {output_path} due to error: \n {e}')




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