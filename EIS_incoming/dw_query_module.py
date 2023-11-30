#General notes, does it for BLF as well because it is coming from the DW

import pyodbc
import pandas as pd

def SQL_query(query):
    odbc_name = 'GD_DW_90'
    conn = pyodbc.connect(f'DSN={odbc_name};')
    df_SQL = pd.read_sql_query(query, con = conn)
    return(df_SQL)


# df = SQL_query('''
# SELECT [SchoolCommonName], [RegionCode], 
# 		[StudentID], [Student_Number], 
# 	   [First_Name], [MiddleName], 
# 	   [Last_Name], [State_StudentNumber], 
# 	   [SSN],[DOB],[EntryDate],[ExitDate]
# FROM [PowerschoolStaged].[dbo].[vw_Rpt_TennStudents]
# WHERE State_StudentNumber = '-----'
# AND EntryDate > '2023-08-01'
# ''')

# df = df.sort_values(by = 'Last_Name').reset_index(drop = True)


# Not present on the 26th but all there on the 27th. One day delay
# Davis, Kylan Jerome  (Now here)
# Doucoure, Khalifa Gueye (Now here)
# Joyner, Shemera ()
# Laury, Terraina Terriouna
# Sample, Payge Ashton