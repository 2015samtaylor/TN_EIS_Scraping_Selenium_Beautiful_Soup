@REM REM Change to the directory containing the Python script
@REM cd "C:\Users\amy.hardy\Desktop\Python_Scripts\EIS_Selenium\EIS_school_error_reports"

@REM REM Run the Python script and redirect output to the log file
@REM "C:\Program Files\Python312\python.exe" EIS_school_error_reports.py



@echo off

REM Redirect all output to output.log
REM (Note: > output.log 2>&1 should be placed where output is generated)

echo [Logging Batch File Output] Running Python script... >> output.log 2>&1

REM Change to the directory containing the Python script
cd "C:\Users\amy.hardy\Desktop\Python_Scripts\EIS_Selenium\EIS_school_error_reports"

REM Run the Python script and redirect output to the log file
"C:\Program Files\Python312\python.exe" EIS_school_error_reports.py >> output.log 2>&1

REM Indicate the process completion
echo Process completed. >> output.log 2>&1