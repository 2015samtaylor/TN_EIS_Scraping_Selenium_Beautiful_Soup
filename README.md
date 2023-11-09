## EIS Student Data Scraper Documentation

### Introduction
This Python script utilizes the Selenium and BeautifulSoup libraries to scrape student data from a web application called "EIS" (Education Information System). It logs into the application, searches for student information based on provided criteria, and extracts relevant data using BeautifulSoup and Selenium. The scraped data is then processed and cleaned using Pandas.

### Prerequisites
Before running the script, ensure that you have the following libraries installed:

- Selenium
- BeautifulSoup
- pandas
- gspread_pandas


ChromeDriver executbale is now a dynamic download within the script, no need to manually download and specify driver location anymore

### Setup and Configuration
1. Define the download directory where the downloaded files will be stored using the `download_directory` variable.
2. Configure Chrome options to set preferences for automatic downloads and specify the download directory.
3. Create a `Service` instance for the Chrome WebDriver, passing the Chrome WebDriver executable path and the defined Chrome options.
4. Create a `webdriver.Chrome` instance by providing the `Service` instance and the Chrome options.
5. Define the `url`, `username`, and `password` variables with appropriate values for logging into the EIS application.

### Who do I talk to?
- Repo owner - Sam Taylor