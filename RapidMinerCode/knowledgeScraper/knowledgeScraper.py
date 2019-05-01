# Import libraries
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import re
import json

# Get all the vocabulary of that page
def vocabList(link, url, end, list_):
    # Connect to the URL
    response = requests.get(link)
    # Parse HTML and save to BeautifulSoup object
    soup = BeautifulSoup(response.text, "html.parser")
    # To download the whole data set, let's do a for loop through all a tags
    voc = soup("div", {"class":"SearchContainer"})
    # If there is at least a vocabulary on that page's list
    if(len(voc)>0):
        # To check the next page
        end += 1
        # Set the index for saving the vocabularies in a list
        index = 0
        # Iterate for every vocabularies present on that page's list
        for i in range(0, len(voc)):
            link = voc[i].a["href"]
            vocabPage(url+link, list_, index)
    # Return the list of vocabularies and the index for the pages
    return list_, end

# Get all the info from the vocabulary page
def vocabPage(link, list_, index):
    # Pause the code for half a sec
    time.sleep(.500)
    # Connect to the URL
    response = requests.get(link)
    # Parse HTML and save to BeautifulSoup object
    soup = BeautifulSoup(response.text, "html.parser")
    
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

    # Get the latest versions and save it with all its relative information
    script = soup("script", {"src": None})[3].text.strip()
    versions = re.compile("{\"events\":(.|\n|\r)*?}]}").search(script)
    if(versions != None):
        versions = json.loads(versions.group(0))["events"]
        # Store the last version with a single line on the list
        i = 0
        for version in range(0, len(versions)):
            # If the version has the relative link for the vocabulary the add it
            if("link" in versions[version].keys()):
                versionName = str(prefix) + "_" + str(i)
                i += 1
                if("title" in versions[version].keys()):
                    versionName = versions[version]["title"].replace(" ","-").replace("\\","").replace("/","").replace(":","").replace("*","").replace("?","").replace("\"","").replace("<","").replace(">","").replace("|","")
                versionDate = ""
                if("start" in versions[version].keys()):
                    versionDate = versions[version]["start"]
                # Create the dictionary for a new version
                versionD = {"prefix": prefix, "URI": uri, "Title": title, "Languages": languages, "VersionName": versionName, "VersionDate": versions[version]["start"], "Link": versions[version]["link"], "Folder": "LOV_Latest"}
                # Add the version to the list
                list_.append(versionD)
                print(versionD)
        # Update the index for the next element of the list
        index += (i/i)
    
    # Return the DataFrame to save the added vocab
    return list_, index

# Mandatory function for RapidMiner
def rm_main():
    # Create the DataFrame to save the LOVs' vocabs' information
    df = pd.DataFrame(columns=["prefix", "URI", "Title", "Languages", "VersionName", "VersionDate", "Link", "Folder"])

    # Set the URL you want to webscrape from
    url = "https://lov.linkeddata.es"
    # Set the starting and ending page to scrape, that updates dynamically
    page = 1
    end = 2
    
    # Scrape every page from the vocabs tab of LOV
    while page < end:
        # Get the #page with the vocabs list
        link = url+"/dataset/lov/vocabs?&page="+str(page)
        # Examine the list of vocabs
        list_, end = vocabList(link, url, end, list())
        # Add the list of that page to the DataFrame, if there are vocabularies in that page
        if(len(list_)):
            df = df.append(list_, ignore_index=True)
        # Iterate the next page if there were vocabs in this page, otherwise end the program there
        page += 1
    
    # Get the other vocabularies from the Excel file from github
    vocabs = pd.read_excel("https://raw.githubusercontent.com/knowdive/resources/master/otherVocabs.xlsx")
    # Create the list used to contain the information about the other vocabularies
    list_ = list()
    index = 0
    # Iterate for every vocabulary read from the Excel file
    for index, row in vocabs.iterrows():
        # Add the vocabulary to the list
        list_.insert(index,{"prefix": row["prefix"], "URI": row["URI"], "Title": row["Title"], "Languages": row["Languages"], "VersionName": row["VersionName"], "VersionDate": row["VersionDate"], "Link": row["Link"], "Folder": row["Folder"]})
        # Update the index for the next element of the list
        index += 1
    # Add the list of that Excel file to the DataFrame, if there are vocabularies in that Excel file
    if(len(list_)):
        df = df.append(list_, ignore_index=True)
    
    # Return the DataFrame for RapidMiner visualization
    return df

print(rm_main())