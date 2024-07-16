import pandas_gbq
import logging
import os

def replicate_BQ_views_to_local(sftp_folder_name, project_id, db, naming_dict, query_template):
    """
    Function to send files to SFTP server from BigQuery tables.
    
    Parameters:
    - sftp: pysftp.Connection object for SFTP connection.
    - dictionary_naming: Dictionary mapping table names to remote filenames.
    - sftp_folder_name: Remote folder name on SFTP server.
    - project_id: Google Cloud project ID for BigQuery.
    """

    # Iterate over dictionary of table names and filenames
    for table_name, remote_filename in naming_dict.items():

        query = query_template.format(project_id=project_id, db=db, table_name=table_name)

        try:
            # Execute the query and store the result in a DataFrame
            df = pandas_gbq.read_gbq(query, project_id=project_id)
        except Exception as e:
            logging.error(f'Error querying table "{table_name}": {str(e)}')
            continue

        # Create nested folder based on sftp_folder_name
        os.makedirs(sftp_folder_name, exist_ok=True)
        logging.info('Directory sftp_file_transfer created or already exists')

        # Write files to local dir
        local_path = os.path.join(sftp_folder_name, remote_filename)
        try:
            df.to_csv(local_path, index=False)
            logging.info(f'File {table_name} being written to local dir {local_path}')
        except Exception as e:
            logging.error(f'File {table_name} unable to be written to local dir {local_path}: {str(e)}')