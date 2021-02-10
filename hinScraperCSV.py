import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
import queue
import html5lib
import json
import re
import time
import os

from datetime import date

# Parameters
login = {'login': '', 'PWDpassword': ''}

"""
def scrape_csv function receives a csv filepath and processes the information into a dataframe. It then scrapes the 
information from a website and returns a dataframe object AND amount of hins processed

:param str fileLocation: location of the csv file needing to be processed

"""
def scrape_csv(fileLocation):

    df = pd.read_csv(fileLocation)
    hin_list = df['HIN_NUM']
    hin_list = set(hin_list)

    base_url = 'https://www.hibcchin.org/hin_detail.asp?hin='
    dfCSV = pd.DataFrame(columns=['HIN NUMBER', 'CUSTOMER NAME', 'ADDRESS LINE 1',
    'ADDRESS LINE 2', 'CITY', 'STATE', 'ZIP CODE', 'COUNTRY', 'MARKET SEGMENT', 'STATUS', 'PHONE NUMBER'])

    # For loop through all the hin list until finished
    for h in hin_list:
        try:
            page = requests.get(base_url + str(h), login, stream=True, verify=False)
        except requests.ConnectionError as e:
            logging.error("** Connection Error **")
            logging.error(str(e))
    
        soup = BeautifulSoup(page.content, features='lxml')
        html = list(soup.children)[0]
        body = list(html.children)[1]

        try:
            # Finds the location of HIN, Customer name, Address 1+2, City State
            # Zipcode, Country
            t2 = list(body.table.table.table)[1]
            subtable = list(t2.children)[0].table
            subtable.b.text   
            t3 = list(subtable.td.td.children)

            # Finds the Market Segment, Status, and Phone number and saves them in variables
            ls = soup.find_all("b")
            MARKET_SEGMENT = str(ls[3]).replace('<b>', '').replace('</b>', '')
            STATUS = str(ls[5]).replace('<b>', '').replace('</b>', '')
            PHONE_NUMBER = str(ls[7]).replace('<b>', '').replace('</b>', '')

            # Phone Number: removing encoded values in the phone number by extracting the integers
            temp = re.findall(r'\d+', PHONE_NUMBER)
            res = list(map(int, temp))
            PHONE_NUMBER = ""
            for x in res:
                PHONE_NUMBER += str(x) + " "

            if len(t3) == 12:
                CUSTOMER_NAME = t3[0].text
                ADDRESS_LINE_1 = t3[1]
                ADDRESS_LINE_2 = t3[3]
                CITYSTATE = t3[5]
                CITY = CITYSTATE.split(',')[0]
                STATE = CITYSTATE.split(',')[1]
                ZIP_CODE = t3[7]
                COUNTRY = t3[9]
            elif len(t3) == 10:
                CUSTOMER_NAME = t3[0].text
                ADDRESS_LINE_1 = t3[1]
                ADDRESS_LINE_2 = ''
                CITYSTATE = t3[3]
                CITY = CITYSTATE.split(',')[0]
                STATE = CITYSTATE.split(',')[1]
                ZIP_CODE = t3[5]
                COUNTRY = t3[7]

            dfCSV = dfCSV.append({'HIN NUMBER': str(h), 'CUSTOMER NAME': CUSTOMER_NAME, 'ADDRESS LINE 1': ADDRESS_LINE_1,
            'ADDRESS LINE 2': ADDRESS_LINE_2, 'CITY': CITY, 'STATE': STATE, 'ZIP CODE': ZIP_CODE, 'COUNTRY': COUNTRY, 
            'MARKET SEGMENT': MARKET_SEGMENT, 'STATUS': STATUS, 'PHONE NUMBER': PHONE_NUMBER}, ignore_index=True)

        except IndexError:
            CUSTOMER_NAME = ''
            ADDRESS_LINE_1 = ''
            ADDRESS_LINE_2 = ''
            CITY = ''
            STATE = ''
            ZIP_CODE = ''
            COUNTRY = ''
            MARKET_SEGMENT = ''
            STATUS = ''
            PHONE_NUMBER = ''

            dfCSV = dfCSV.append({'HIN NUMBER': str(h), 'CUSTOMER NAME': CUSTOMER_NAME, 'ADDRESS LINE 1': ADDRESS_LINE_1,
            'ADDRESS LINE 2': ADDRESS_LINE_2, 'CITY': CITY, 'STATE': STATE, 'ZIP CODE': ZIP_CODE, 'COUNTRY': COUNTRY, 
            'MARKET SEGMENT': MARKET_SEGMENT, 'STATUS': STATUS, 'PHONE NUMBER': PHONE_NUMBER}, ignore_index=True)

    # Exiting For loop to save processed information from dataframe to csv file
    dfCSV.to_csv(fileLocation, index = False, header = True)

    # Returns the completed dataframe AND number of hins processed for time saved value
    return(dfCSV, len(hin_list))