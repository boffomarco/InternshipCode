# Import libraries
from bs4 import BeautifulSoup
from pathlib import Path
import requests
import urllib.request
import time
import pandas as pd
import re
import json
import os

# Class to handle the Excel file and relative index
class ExcelFile:
  def __init__(self, writer):
    self.writer = writer
    self.index = 1

# Get all the vocabulary of that page
def vocabList(link, url, end, excel):
    # Connect to the URL
    response = requests.get(link)
    # Parse HTML and save to BeautifulSoup object
    soup = BeautifulSoup(response.text, "html.parser")
    # To download the whole data set, let's do a for loop through all a tags
    voc = soup("div", {"class":"SearchContainer"})
    # if there is at least a vocabulary on that page's list
    if(len(voc)>0):
        # To check the next page
        end += 1
        # Iterate for every vocabularies present on that page's list
        for i in range(0, len(voc)):
            link = voc[i].a["href"]
            vocabPage(url+link, excel)
    return end

# Get all the info and the N3 from the vocabulary page
def vocabPage(link, excel):
    # Pause the code for half a sec
    time.sleep(.500)
    # Connect to the URL
    response = requests.get(link)
    # Parse HTML and save to BeautifulSoup object
    soup = BeautifulSoup(response.text, "html.parser")

    # Get the excel file and relative worksheets
    workbook = excel.writer.book
    sheet = workbook.get_worksheet_by_name("LOVVersions")
    
    # Get the title and prefix from the vocabulary page
    title = soup("h1")[0]
    prefix = title.span.extract().text.strip()
    title = title.text.strip()
    prefix = prefix.replace("(", "").replace(")", "")
    #Get the URI and Languages from the vocabulary page
    uri = "URI"
    languages = " "
    for child in soup("tbody")[0].find_all("tr"):
        # Get the URI
        if child.td.text.strip() == "URI":
            uri = child.find_all("td")[1].text.strip() 
        # Get the Languages
        if child.td.text.strip() == "Language":
            language = child.find_all("td")[1]
            # Append the Languages with a space as separator
            for childL in language.find_all("a"):
                nameL = childL.find("div", {"class": "agentThumbPrefUri"}).text.strip()
                languages += nameL+" "

    # Get all the versions and save them with all their relative informations
    script = soup("script", {"src": None})[3].text.strip()
    versions = re.compile("{\"events\":(.|\n|\r)*?}]}").search(script)
    if(versions != None):
        versions = json.loads(versions.group(0))["events"]
        # Store every version with a line on the Excel File
        index = 0
        for version in range(0, len(versions)):
            if("title" in versions[version].keys() and "start" in versions[version].keys() and "link" in versions[version].keys()):
                versionName = versions[version]["title"].replace(" ","-").replace("\\","").replace("/","").replace(":","").replace("*","").replace("?","").replace("\"","").replace("<","").replace(">","").replace("|","")
                sheet.write_row(excel.index, 0, (prefix, uri, title, languages, versionName, versions[version]["start"], versions[version]["link"], "LOV_Latest"))
                index = 1
        excel.index += index


# Mandatory function for RapidMiner
def rm_main(data):
    # Get the destination folder and file name from RapidMiner
    location = "C:\\Users\\marco\\Desktop\\Internship\\Results"
    destination = "LOV_Latest"
    if(len(data)):
        location = data.iloc[0,0]
        destination = data.iloc[0,1]
    if not os.path.isdir(location):
        os.makedirs(location)

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(str(os.path.join(location, destination)) + ".xlsx", engine='xlsxwriter')
    excel = ExcelFile(writer)
    # Get the xlsxwriter workbook and worksheet objects.
    workbook  = writer.book
    # Add WorkSheet with relative titles and relative bold header 
    sheet = workbook.add_worksheet("LOVVersions")
    sheet.write_row(0, 0, ("prefix", "URI", "Title", "Languages", "VersionName", "VersionDate", "Link", "Folder"), workbook.add_format({"bold": True}))
    sheet.set_column(0, 6, 30)

    # Set the URL you want to webscrape from
    url = "https://lov.linkeddata.es"
    # Set the starting and ending page to scrape, that updates dynamically
    page = 1
    end = 2

    # Scrape every page from the vocabs tab of LOV
    while page < end:
        # Get the #page with the vocabs list
        link = url+"/dataset/lov/vocabs?&page="+str(page)
        end = vocabList(link, url, end, excel)
        # Iterate the next page if there were vocabs in this page, otherwise end the program there
        page += 1

    # Close and save the Excel file
    workbook.close()
    writer.save()

rm_main(pd.read_excel(r"C:\Users\marco\Desktop\Internship\IN.xlsx", sheet_name=0, header=None))