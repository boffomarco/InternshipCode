# Import libraries
from bs4 import BeautifulSoup
from pathlib import Path
import requests
import urllib.request
import time
import pandas as pd
import re
import json


# Class to handle the Excel file and relative indexes
class ExcelFile:
  def __init__(self, writer):
    self.writer = writer
    self.metaIndex = 1
    self.langIndex = 1
    self.creIndex = 1
    self.contIndex = 1
    self.pubIndex = 1
    self.expIndex = 1
    self.tagsIndex = 1
    self.linksIndex = 1

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
        # Iterate for every vocabularies of that page's list
        for i in range(0, len(voc)):
            # Pause the code for a sec
            time.sleep(.500) 
            link = voc[i].a["href"]
            vocabPage(url+link, excel)
    return end

# Get all the info and the N3 from the vocabulary page
def vocabPage(link, excel):
    # Pause the code for a sec
    time.sleep(.500)
    # Connect to the URL
    response = requests.get(link)
    # Parse HTML and save to BeautifulSoup object
    soup = BeautifulSoup(response.text, "html.parser")
    # Download the vocabulary N3
    notation3 = soup("div", {"style":"float:left; padding-left:0.5em; border-right:1px solid white"})
    # Check if the N3 file is really present in the vocabulary page 
    if(len(notation3)>0):
        try:
            # Extract the directory path to store the data
            dir = Path(__file__).parents[2]
            urllib.request.urlretrieve(notation3[0].a["href"],str(dir) + "/Resources/LOV/" + notation3[0].img["title"].replace(" ","_")  + ".n3")
        except:
            log("Error trying to get " + notation3[0].a["href"]+"\n")
    else:
        log("No N3 file found for " + soup("header", {"class":"wrpl w-3-3"})[0].a["href"] + "\n")
    # Get all the other info about that vocabulary 
    vocabMeta(soup, excel)

# Get all the info from the vocabulary page
def vocabMeta(soup, excel):
    # Get the excel file and relative worksheets
    workbook = excel.writer.book
    meta = workbook.get_worksheet_by_name("Metadata")
    languages = workbook.get_worksheet_by_name("Languages")
    creators = workbook.get_worksheet_by_name("Creators")
    contributors = workbook.get_worksheet_by_name("Contributors")
    publishers = workbook.get_worksheet_by_name("Publishers")
    expressivity = workbook.get_worksheet_by_name("Expressivity")
    tags = workbook.get_worksheet_by_name("Tags")
    links = workbook.get_worksheet_by_name("Links")
    
    # Get the title and prefix of the vocabulary 
    title = soup("h1")[0]
    prefix = title.span.extract().text.strip()
    title = title.text.strip()
    prefix = prefix.replace("(", "").replace(")", "")
    
    #Get the Metadata, Language, Creator, Contributor, Publisher of the vocabulary page
    uri = "URI"
    namespace = "Namespace"
    homepage = "homepage"
    description = "Description"
    for child in soup("tbody")[0].find_all("tr"):
        if child.td.text.strip() == "URI":
            uri = child.find_all("td")[1].text.strip() 
        if child.td.text.strip() == "Namespace":
            namespace = child.find_all("td")[1].text.strip() 
        if child.td.text.strip() == "homepage":
            homepage = child.find_all("td")[1].text.strip() 
        if child.td.text.strip() == "Description":
            description = child.find_all("td")[1].text.strip() 
        if child.td.text.strip() == "Language":
            language = child.find_all("td")[1]
            # Add the Languages of the vocabulary page to the excel file
            for childL in language.find_all("a"):
                nameL = childL.find("div", {"class": "agentThumbName"}).text.strip()
                uriL = childL.find("div", {"class": "agentThumbPrefUri"}).text.strip()
                languages.write_row(excel.langIndex, 0, (prefix, nameL, uriL))
                excel.langIndex += 1
        if child.td.text.strip() == "Creator":
            creator = child.find_all("td")[1]
            # Add the Creators of the vocabulary page to the excel file
            for childCr in creator.find_all("a"):
                nameCr = childCr.find("div", {"class": "agentThumbName"}).text.strip()
                uriCr = childCr.find("div", {"class": "agentThumbPrefUri"}).text.strip()
                creators.write_row(excel.creIndex, 0, (prefix, nameCr, uriCr))
                excel.creIndex += 1
        if child.td.text.strip() == "Contributor":
            contributor = child.find_all("td")[1]
            # Add the Contributors of the vocabulary page to the excel file
            for childCo in contributor.find_all("a"):
                nameCo = childCo.find("div", {"class": "agentThumbName"}).text.strip()
                uriCo = childCo.find("div", {"class": "agentThumbPrefUri"}).text.strip()
                contributors.write_row(excel.contIndex, 0, (prefix, nameCo, uriCo))
                excel.contIndex += 1
        if child.td.text.strip() == "Publisher":
            publisher = child.find_all("td")[1]
            # Add the Publishers of the vocabulary page to the excel file
            for childP in publisher.find_all("a"):
                nameP = childP.find("div", {"class": "agentThumbName"}).text.strip()
                uriP = childP.find("div", {"class": "agentThumbPrefUri"}).text.strip()
                publishers.write_row(excel.pubIndex, 0, (prefix, nameP, uriP))
                excel.pubIndex += 1

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

        # Add the Metadata of the vocabulary page to the excel file
        meta.write_row(excel.metaIndex, 0, (prefix, title, uri, namespace, homepage, description, classes, properties, datatypes, instances))
        excel.metaIndex += 1

    # Add the Expressivity of the vocabulary page to the excel file
    exp = soup("ul", {"class": "expressivities"})
    if(exp):    
        for child in exp[0].find_all("li"):
            expressivity.write_row(excel.expIndex, 0, (prefix, child.text.strip()))
            excel.expIndex += 1

    # Add the Tags of the vocabulary page to the excel file
    tag = soup("ul", {"class": "tagsVocab"})
    if(tag):
        for child in tag[0].find_all("li"):
            tags.write_row(excel.tagsIndex, 0, (prefix, child.text.strip()))
            excel.tagsIndex += 1

    # Add the Links of the vocabulary page to the excel file
    script = soup("script", {"src": None})[1].text.strip()
    incomingLinks = re.compile("var graphIn = ((.|\n|\r)*?);")
    incomingLinks = json.loads(incomingLinks.search(script).group(1))["nodes"]
    for link in range(1, len(incomingLinks)):
        links.write_row(excel.linksIndex, 0, (prefix, "incoming", getLinkType(incomingLinks[link]["group"]), incomingLinks[link]["name"]))
        excel.linksIndex += 1
    outgoingLinks = re.compile("var graph = ((.|\n|\r)*?);")
    outgoingLinks = json.loads(outgoingLinks.search(script).group(1))["nodes"]
    for link in range(1, len(outgoingLinks)):
        links.write_row(excel.linksIndex, 0, (prefix, "outgoing", getLinkType(outgoingLinks[link]["group"]), outgoingLinks[link]["name"]))
        excel.linksIndex += 1

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

# Logs the date with the string str to track errors 
def log(str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S - ", time.gmtime())
    f = open("log.txt", "a+")
    f.write(ts + str)
    f.close()