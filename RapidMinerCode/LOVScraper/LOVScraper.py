# Import libraries
from bs4 import BeautifulSoup
from pathlib import Path
import requests
import urllib.request
import time
import pandas as pd

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
        index = 0
        # Iterate for every vocabularies of that page's list
        for i in range(0, len(voc)):
            link = voc[i].a["href"]
            # Check the vocabPage to get the Name and Link
            list_, index = vocabPage(url+link, list_, index)
    # Return the DataFrame and the index
    return list_, end

# Get all the info and the N3 from the vocabulary page
def vocabPage(link, list_, index):
    # Pause the code for half a sec
    time.sleep(.500)
    # Connect to the URL
    response = requests.get(link)
    # Parse HTML and save to BeautifulSoup object
    soup = BeautifulSoup(response.text, "html.parser")
    # Download the vocabulary N3
    notation3 = soup("div", {"style":"float:left; padding-left:0.5em; border-right:1px solid white"})
    # Check if the N3 file is really present in the vocabulary page 
    if(len(notation3)>0):
        # Try to save the 
        list_.insert(index,{"Name": notation3[0].img["title"].replace(" ","_"), "Link": notation3[0].a["href"], "File": "LOV"})
        index += 1
        # Log the added vocabulary
        log("Added " + notation3[0].img["title"].replace(" ","_")+"\n")
    else:
        # Log the vocabulary with no file
        log("No N3 file found for " + soup("header", {"class":"wrpl w-3-3"})[0].a["href"] + "\n")
    # Return the DataFrame to save the added vocab
    return list_, index

# Logs the date with the string str to track errors 
def log(str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S - ", time.gmtime())
    f = open("log.txt", "a+")
    f.write(ts + str)
    f.close()

def rm_main():
    # Create the DataFrame to save the "LOVs' name and link
    df = pd.DataFrame(columns=["Name", "Link", "File"])

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
        df = df.append(list_)
        # Iterate the next page if there were vocabs in this page, otherwise end the program here
        page += 1

    # Convert the DataFrame to csv
    df.to_csv("LOVvocabs.csv")
    df.to_excel("LOVvocabs.xlsx", sheet_name = "Data")

    # Return the DataFrame for RapidMiner visualization
    return df

rm_main()