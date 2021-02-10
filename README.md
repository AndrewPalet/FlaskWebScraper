# Flask Web Application
Automation that scrapes HIN (Health Industry Number) information from the website (https://www.hibcchin.org). After completing the webscraping the application logs its results in Azure blob storage to metrics and error tracking.

This is a web application that uses Flask framework. I written the app server in python and the layouts using html/CSS/javascript.

# Web Application In Action
Steps
* Read instructions, then download a csv template and fill out the information you're wanting to scrape
* Upload the file to the application. Web app injests the csv and iterates through your request
* Web app constructs a csv with the recently scraped information to be served back to the user
* Completed csv is prompted to the user for download to their pc

![Flask Web Scraper Screenshot](https://github.com/AndrewPalet/FlaskWebScraper/blob/master/static/img/WebAppScreenshot.PNG "Flask Web Scraper Screenshot")

# Skills Demonstrated
    - Flask framework
    - Python
    - HTML/CSS/Javascript
    - Azure blob storage and logging
    - Web Scraping using requests and beautifulsoup