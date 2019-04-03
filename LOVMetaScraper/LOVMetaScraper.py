# Import libraries
from bs4 import BeautifulSoup
from pathlib import Path
import requests
import time
import pandas as pd
import re
import json
import os

# Get all the vocabulary of that page
def vocabList(link, url, end, set_, MDF):
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
            vocabPage(url+link, set_, MDF)
    return end

# Get all the info and the N3 from the vocabulary page
def vocabPage(link, set_, MDF):
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

    checkMeta("prefix", prefix, set_, MDF)
    checkMeta("title", title, set_, MDF)

    #Get the URI and Languages from the vocabulary page
    for child in soup("tbody")[0].find_all("tr"):
        checkMeta(child.td.text.strip(), child.find_all("td")[1].text.strip() , set_, MDF)
    
    # Get the statistics of the vocabulary
    script = soup("script", {"src": None})[2].text.strip()
    stats = re.compile(".datum\((.*?)\)")
    stats = stats.search(script).group(1)
    if(stats):
        stats = json.loads(stats)[0]["values"]
        classes = stats[0]["value"]
        properties = stats[1]["value"]
        datatypes = stats[2]["value"]
        instances = stats[3]["value"]

        checkMeta("classes", classes , set_, MDF)
        checkMeta("properties", properties , set_, MDF)
        checkMeta("datatypes", datatypes , set_, MDF)
        checkMeta("instances", instances , set_, MDF)

    # Add the Expressivity of the vocabulary page to the excel file
    exp = soup("ul", {"class": "expressivities"})[0].find_all("li")
    if(exp):    
        checkMeta("exprs", exp[0].text.strip(), set_, MDF)

    # Add the tagsVocab of the vocabulary page to the excel file
    tag = soup("ul", {"class": "tagsVocab"})[0].find_all("li")
    if(tag):    
        checkMeta("tags", tag[0].text.strip(), set_, MDF)

    # Get all the versions and save them with all their relative informations
    script = soup("script", {"src": None})[3].text.strip()
    versions = re.compile("{\"events\":(.|\n|\r)*?}]}").search(script)
    if(versions != None):
        versions = json.loads(versions.group(0))["events"]
        for version in range(0, len(versions)):
            for v in versions[version].keys():
                checkMeta(v, versions[version][v], set_, MDF)
    

    # Add the Links of the vocabulary page to the excel file
    script = soup("script", {"src": None})[1].text.strip()
    incomingLinks = re.compile("var graphIn = ((.|\n|\r)*?);")
    incomingLinks = json.loads(incomingLinks.search(script).group(1))["nodes"]
    for link in range(1, len(incomingLinks)):
        checkMeta("incoming_"+getLinkType(incomingLinks[link]["group"]), prefix+"_"+getLinkType(incomingLinks[link]["group"])+"_"+incomingLinks[link]["name"], set_, MDF)
    outgoingLinks = re.compile("var graph = ((.|\n|\r)*?);")
    outgoingLinks = json.loads(outgoingLinks.search(script).group(1))["nodes"]
    for link in range(1, len(outgoingLinks)):
        checkMeta("outgoing_"+getLinkType(outgoingLinks[link]["group"]), prefix+"_"+getLinkType(outgoingLinks[link]["group"])+"_"+outgoingLinks[link]["name"], set_, MDF)


# Return the text relative to the link color
def getLinkType(i):
    if i == 0:
        return "Specializes"
    if i == 1:
        return "Generalizes"
    if i == 4:
        return "Extends"
    if i == 6:
        return "Imports"
    if i == 13:
        return "Metadata"
    if i == 14:
        return "HasEquivalencesWith"
    if i == 15:
        return "HasDisjunctionWith"

def checkMeta(metavar, examplevar, set_, MDF):
    # Check if new Names has to be added or if existing Names has to be updated
    a = len(set_)
    meta = metavar
    set_.add(metavar)
    if(a < len(set_)):
        # Create a new row on the DataFrame for that Names
        MDF.at[metavar, "Name"] = metavar
        MDF.at[metavar, "Example"] = examplevar
        MDF.at[metavar, "number"] = 1
    else:
        number = MDF.at[metavar, "number"]
        MDF.at[metavar, "Example"] = examplevar
        MDF.at[metavar, "number"] = number + 1

# Create the DataFrame used to save the table used to identify common Elements between Names
MDF = pd.DataFrame(columns=["Name", "number", "Example"])

# Set the URL you want to webscrape from
url = "https://lov.linkeddata.es"
# Set the starting and ending page to scrape, that updates dynamically
page = 1
end = 2

set_ = set()
# Scrape every page from the vocabs tab of LOV
while page < end:
    # Get the #page with the vocabs list
    link = url+"/dataset/lov/vocabs?&page="+str(page)
    end = vocabList(link, url, end, set_, MDF)
    # Iterate the next page if there were vocabs in this page, otherwise end the program there
    page += 1

MDF.to_excel(os.path.normpath(os.path.expanduser("~/Documents/Internship/LOVMeta.xlsx")))
