# Import libraries
from bs4 import BeautifulSoup
from pathlib import Path
import requests
import time
import pandas as pd
import re
import json
import ckanapi

import pprint

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

# Get all the vocabulary of that page
def vocabList(link, url, end, groupId):
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
            oldLink = link
            link = voc[i].a["href"]
            if(link != oldLink):
                vocabPage(url+link, groupId)
    return end

# Get all the info and the N3 from the vocabulary page
def vocabPage(link, groupId):
    # Pause the code for a sec
    time.sleep(.500)
    # Connect to the URL
    response = requests.get(link)
    # Parse HTML and save to BeautifulSoup object
    soup = BeautifulSoup(response.text, "html.parser")
    # Get all the other info about that vocabulary 
    vocabMeta(soup, groupId)

# Get all the info from the vocabulary page
def vocabMeta(soup, groupId):

    mysite = ckanapi.RemoteCKAN('http://streambase7.disi.unitn.it:5000',
        apikey='873daee2-3cd4-4621-9079-730f01609ce1',
        user_agent='liveschema/1.0 (+http://liveschema.org/)')

    # Get the title and prefix of the vocabulary 
    title = soup("h1")[0]
    prefix = title.span.extract().text.strip()
    title = title.text.strip()
    prefix = prefix.replace("(", "").replace(")", "").decode('utf-8').lower()
    prefix = ''.join([i for i in prefix if (i.isdigit() or i.isalpha() or i==" " or i=="_" or i == "-")])
    organization = dict(name= "lov_"+prefix, title= title)
    package = dict(extras=list(), groups=[{"name": groupId}])

    #Get the Metadata, Language, Creator, Contributor, Publisher of the vocabulary page
    uri = "URI"
    namespace = "Namespace"
    homepage = "homepage"
    description = "Description"
    languages = list()
    pub = 1
    for child in soup("tbody")[0].find_all("tr"):
        if child.td.text.strip() == "URI":
            uri = child.find_all("td")[1].text.strip() 
            package["extras"].append({"key": "uri", "value": uri})
        if child.td.text.strip() == "Namespace":
            namespace = child.find_all("td")[1].text.strip() 
            package["url"] = namespace
        if child.td.text.strip() == "homepage":
            homepage = child.find_all("td")[1].text.strip() 
            package["extras"].append({"key": "contact_uri", "value": homepage})
        if child.td.text.strip() == "Description":
            description = child.find_all("td")[1].text.strip() 
            organization["description"] = description
            package["notes"] = description
        # Get the Languages
        if child.td.text.strip() == "Language":
            language = child.find_all("td")[1]
            # Append the Languages with a space as separator
            for childL in language.find_all("a"):
                uriL = childL.find("div", {"class": "agentThumbPrefUri"}).text.strip()
                languages.append(uriL)
            package["extras"].append({"key": "language", "value": languages})

        if child.td.text.strip() == "Publisher" and pub:
            publisher = child.find_all("td")[1]
            # Add the first Publishers of the vocabulary page to the excel file
            for childP in publisher.find_all("a"):
                nameP = childP.find("div", {"class": "agentThumbName"}).text.strip()
                uriP = childP.find("div", {"class": "agentThumbPrefUri"}).text.strip()
                package["extras"].append({"key": "publisher_uri", "value": uriP})
                package["extras"].append({"key": "publisher_name", "value": nameP})
                package["extras"].append({"key": "publisher_url", "value": uriP})
                package["extras"].append({"key": "publisher_type", "value": "Publisher"})
                pub = 0
                break
        elif child.td.text.strip() == "Creator" and pub:
            creator = child.find_all("td")[1]
            # Add the Creators of the vocabulary page to the excel file
            for childCr in creator.find_all("a"):
                nameCr = childCr.find("div", {"class": "agentThumbName"}).text.strip()
                uriCr = childCr.find("div", {"class": "agentThumbPrefUri"}).text.strip()
                package["extras"].append({"key": "publisher_uri", "value": uriCr})
                package["extras"].append({"key": "publisher_name", "value": nameCr})
                package["extras"].append({"key": "publisher_url", "value": uriCr})
                package["extras"].append({"key": "publisher_type", "value": "Creator"})
                pub = 0
                break
        elif child.td.text.strip() == "Contributor" and pub:
            contributor = child.find_all("td")[1]
            # Add the Contributors of the vocabulary page to the excel file
            for childCo in contributor.find_all("a"):
                nameCo = childCo.find("div", {"class": "agentThumbName"}).text.strip()
                uriCo = childCo.find("div", {"class": "agentThumbPrefUri"}).text.strip()
                package["extras"].append({"key": "publisher_uri", "value": uriCo})
                package["extras"].append({"key": "publisher_name", "value": nameCo})
                package["extras"].append({"key": "publisher_url", "value": uriCo})
                package["extras"].append({"key": "publisher_type", "value": "Contributor"})
                pub = 0
                break
    
    org = mysite.call_action("organization_create", organization)
    package["owner_org"] = org["id"]

    # Add the Tags of the vocabulary page to the excel file
    tag = soup("ul", {"class": "tagsVocab"})
    tags = list()
    if(tag):
        for child in tag[0].find_all("li"):
            tagName = child.text.strip().decode('utf-8').lower()
            tagName = ''.join([i for i in tagName if (i.isdigit() or i.isalpha() or i==" " or i=="_" or i == "-")])
            tags.append({"name": tagName})
        package["tags"] = tags

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

        packStats = "Classes: " + str(classes) + " - "
        packStats = packStats + "Properties: " + str(properties) + " - "
        packStats = packStats + "DataTypes: " + str(datatypes) + " - "
        packStats = packStats + "Instances: " + str(instances)

        package["extras"].append({"key": "Statistics", "value": packStats})

    # Add the Expressivity of the vocabulary page to the excel file
    exp = soup("ul", {"class": "expressivities"})
    if(exp):
        packExpr = ""
        for child in exp[0].find_all("li"):
            packExpr = packExpr + child.text.strip().decode('utf-8').lower() + " - "
        package["extras"].append({"key": "Expressivity", "value": packExpr})

    # Add the Links of the vocabulary page to the excel file
    script = soup("script", {"src": None})[1].text.strip()
    incomingLinks = re.compile("var graphIn = ((.|\n|\r)*?);")
    incomingLinks = json.loads(incomingLinks.search(script).group(1))["nodes"]
    packIn = ""
    for link in range(1, len(incomingLinks)):
        packIn = packIn + getLinkType(incomingLinks[link]["group"]) + " -> " + incomingLinks[link]["name"] + " - "
    package["extras"].append({"key": "Incoming Links", "value": packIn})
    outgoingLinks = re.compile("var graph = ((.|\n|\r)*?);")
    outgoingLinks = json.loads(outgoingLinks.search(script).group(1))["nodes"]
    packOut = ""
    for link in range(1, len(outgoingLinks)):
        packOut = packOut + getLinkType(outgoingLinks[link]["group"]) + " -> " + outgoingLinks[link]["name"] + " - "
    package["extras"].append({"key": "Outgoing Links", "value": packOut})
    
    # Get all the versions and save them with all their relative informations
    script = soup("script", {"src": None})[3].text.strip()
    versions = re.compile("{\"events\":(.|\n|\r)*?}]}").search(script)
    if(versions != None):
        versions = json.loads(versions.group(0))["events"]
        index = 0
        # Store every version with a line on the Excel File
        for version in range(0, len(versions)):
            
            if("version" in package.keys()):
                del package["version"]
            if("url" in package.keys()):
                del package["url"]
            package["extras"] = [i for i in package["extras"] if not ((i["key"] == "issued") or (i["key"] == "modified"))] 

            versionName = ""
            if("title" in versions[version].keys() and "start" in versions[version].keys() and "link" in versions[version].keys()):
                versionName = versions[version]["title"].replace(" ","-").replace(".","-").replace(";","-").replace("\\","").replace("/","").replace(":","").replace("*","").replace("?","").replace("\"","").replace("<","").replace(">","").replace("|","")
                package["version"] = versionName
            if("link" in versions[version].keys()):
                versionLink = versions[version]["link"]
                package["url"] = versionLink
                package["extras"].append({"key": "linkVersion_" + str(index), "value": versionLink})
            if("start" in versions[version].keys()):
                versionStart = versions[version]["start"]
                package["extras"].append({"key": "issued", "value": versionStart})
            if("end" in versions[version].keys()):
                versionEnd = versions[version]["end"]
                package["extras"].append({"key": "modified", "value": versionEnd})
            
            package["name"] = "lov_" + prefix + "_" + versionName.decode('utf-8').lower() + "_" + str(index)
            package["title"] = title + " " + versionName
            index += 1

        #pprint.pprint(package)
        print(package["name"])
        mysite.call_action("package_create", package)

    log("Saved " + prefix + "\n")
    del package
    del organization

# Logs the date with the string str to track errors 
def log(str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S - ", time.gmtime())
    f = open("log.txt", "a+")
    f.write(ts + str)
    f.close()

#Clean the database
mysite = ckanapi.RemoteCKAN('http://streambase7.disi.unitn.it:5000',
    apikey='873daee2-3cd4-4621-9079-730f01609ce1',
    user_agent='liveschema/1.0 (+http://liveschema.org/)')

e = mysite.call_action('package_list')
for pack in e:
    p = mysite.call_action('package_show', {"id": pack})
    mysite.call_action('dataset_purge', {"id": p["id"]})

e = mysite.call_action('organization_list')
for org in e:
    o = mysite.call_action('organization_show', {"id": org})
    mysite.call_action('organization_purge', {"id": o["id"]})

# Set the URL you want to webscrape from
url = "https://lov.linkeddata.es"
# Set the starting and ending page to scrape, that updates dynamically
page = 1
end = 2

group = mysite.call_action('group_create', 
    {"name": "lov",
    "id": "lov",
    "title": "LinkedOpenVocabulary"})

# Scrape every page from the vocabs tab of LOV
while page < end:
    # Get the #page with the vocabs list
    link = url+"/dataset/lov/vocabs?&page="+str(page)
    end = vocabList(link, url, end, group["id"])
    # Iterate the next page if there were vocabs in this page, otherwise end the program here
    page += 1


# otherVocabScraper
