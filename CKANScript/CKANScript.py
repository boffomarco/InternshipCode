# Import libraries
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import re
import json
import ckanapi
import os
import rdflib
from rdflib import Graph, Namespace
from rdflib.util import guess_format
from rdflib.plugins.parsers.notation3 import N3Parser

# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')


# Script to scrape the Others excel file from github
def scrapeOthers(CKAN, CKAN_URL, CKAN_KEY, catalogs, datasets):
    # Check if the Others excel file from github is present on LiveSchema
    cataOthers = ""
    if "other" in catalogs:
        # If it is then get its relative information and datasets
        cataOthers = CKAN.call_action('organization_show', {"id": "other", "include_datasets": False, "include_dataset_count": False, "include_extras": False, "include_users": False, "include_groups": False, "include_tags": False, "include_followers": False})
    else:
        # Otherwise create the catalog for the Other excel file from github
        cataOthers = CKAN.call_action('organization_create', 
        {"name": "other",
        "id": "other",
        "title": "Other Vocabularies",
        "state": "active",
        "extras": [{"key": "URL", "value": "https://github.com/knowdive/resources/blob/master/otherVocabs.xlsx"}]})

    # Get the other vocabularies from the Excel file from github
    vocabs = pd.read_excel("https://raw.githubusercontent.com/knowdive/resources/master/otherVocabs.xlsx")
    # Iterate for every vocabulary read from the Excel file
    for index, row in vocabs.iterrows():

        # Get the title and prefix of the vocabulary 
        package = dict(extras=list())

        # Add the metadata of the dataset
        package["url"] = row["Link"]

        package["name"] = "other_" + row["prefix"].lower().replace(" ","-").replace(".","-").replace(";","-").replace("\\","").replace("/","").replace(":","").replace("*","").replace("?","").replace("\"","").replace("<","").replace(">","").replace("|","")
        
        package["title"] = row["prefix"]
        package["notes"] = row["Title"]

        package["owner_org"] = cataOthers["id"]

        package["version"] = row["VersionName"]
        package["extras"].append({"key": "issued", "value": row["VersionDate"]})
        package["extras"].append({"key": "language", "value": row["Languages"]})

        package["extras"].append({"key": "contact_uri", "value": row["URI"]})

        log(json.dumps(package))
        # Check if the dataset has to be updated
        checkPackage(CKAN, CKAN_URL, CKAN_KEY, datasets, package)


# Script to scrape the LOV repository
def scrapeLOV(CKAN, CKAN_URL, CKAN_KEY, catalogs, datasets):
    # Check if LOV is present on LiveSchema
    cataLOV = ""
    if "lov" in catalogs:
        # If it is then get its relative information and datasets
        cataLOV = CKAN.call_action('organization_show', {"id": "lov", "include_datasets": False, "include_dataset_count": False, "include_extras": False, "include_users": False, "include_groups": False, "include_tags": False, "include_followers": False})
    else:
        # Otherwise create the catalog for LOV
        cataLOV = CKAN.call_action('organization_create', 
            {"name": "lov",
            "id": "lov",
            "state": "active",
            "title": "Linked Open Vocabulary",
            "image_url": "https://lov.linkeddata.es/img/icon-LOV.png",
            "extras": [{"key": "URL", "value": "https://lov.linkeddata.es/dataset/lov"}],
            "description": "LOV started in 2011, in the framework of a French research project (http://datalift.org). Its main initial objective was to help publishers and users of linked data and vocabularies to assess what was available for their needs, to reuse it as far as possible, and to insert their own vocabulary production seamlessly in the ecosystem."})

    # Set the URL you want to webscrape from
    url = "https://lov.linkeddata.es"
    # Set the starting and ending page to scrape, that updates dynamically
    page = 1
    end = 2

    # Scrape every page from the vocabs tab of LOV
    while page < end:
        # Get the #page with the vocabs list
        link = url+"/dataset/lov/vocabs?&page="+str(page)
        end = vocabList(CKAN, CKAN_URL, CKAN_KEY, cataLOV, datasets, link, url, end)
        # Iterate the next page if there were vocabs in this page, otherwise end the program here
        page += 1

# Get all the vocabulary of that page
def vocabList(CKAN, CKAN_URL, CKAN_KEY, cataLOV, datasets, link, url, end):
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
            #time.sleep(.500) 
            #oldLink = link
            link = voc[i].a["href"]
            vocabMeta(CKAN, CKAN_URL, CKAN_KEY, cataLOV, datasets, url+link)
    return end

# Get all the info from the vocabulary page
def vocabMeta(CKAN, CKAN_URL, CKAN_KEY, cataLOV, datasets, link):
    # Pause the code for a sec
    #time.sleep(.500)
    # Connect to the URL
    response = requests.get(link)
    # Parse HTML and save to BeautifulSoup object
    soup = BeautifulSoup(response.text, "html.parser")

    # Get the title and prefix of the vocabulary 
    title = soup("h1")[0]
    prefix = title.span.extract().text.strip()
    title = title.text.strip()
    prefix = prefix.replace("(", "").replace(")", "").decode('utf-8').lower()
    prefix = ''.join([i for i in prefix if (i.isdigit() or i.isalpha() or i==" " or i=="_" or i == "-")])
    # Create the package as a dict
    package = dict(extras=list())
    # Add the basic metadata of the dataset
    package["name"] = "lov_" + prefix
    package["title"] = title
    package["owner_org"] = cataLOV["id"]
    package["extras"].append({"key": "Reference Catalog URL", "value": link})

    #Get the Metadata and Languages of the vocabulary page
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
            package["notes"] = description
        # Get the Languages
        if child.td.text.strip() == "Language":
            language = child.find_all("td")[1]
            # Append the Languages with a space as separator
            for childL in language.find_all("a"):
                uriL = childL.find("div", {"class": "agentThumbPrefUri"}).text.strip()
                languages.append(uriL)
            package["extras"].append({"key": "language", "value": ', '.join(languages)})

    # Add the Tags of the vocabulary page to the excel file
    tag = soup("ul", {"class": "tagsVocab"})
    tags = list()
    if(tag):
        for child in tag[0].find_all("li"):
            tagName = child.text.strip().decode('utf-8').lower()
            tagName = ''.join([i for i in tagName if (i.isdigit() or i.isalpha() or i==" " or i=="_" or i == "-")])
            tags.append({"name": tagName})
        package["tags"] = tags

    # Get all the versions and save them with all their relative informations
    script = soup("script", {"src": None})[3].text.strip()
    versions = re.compile("{\"events\":(.|\n|\r)*?}]}").search(script)
    if(versions != None):
        # Store every version with a line on the Excel File
        versions = json.loads(versions.group(0))["events"]
        for version in range(0, len(versions)):
            if("version" in package.keys()):
                del package["version"]
            package["extras"] = [i for i in package["extras"] if not ((i["key"] == "issued") or (i["key"] == "modified"))] 

            versionName = ""
            if("title" in versions[version].keys() and "start" in versions[version].keys() and "link" in versions[version].keys() and "link" in versions[version].keys()):
                versionName = versions[version]["title"].replace(" ","-").replace(".","-").replace(";","-").replace("\\","").replace("/","").replace(":","").replace("*","").replace("?","").replace("\"","").replace("<","").replace(">","").replace("|","")
                package["version"] = versionName
                versionLink = versions[version]["link"]
                package["url"] = versionLink
            if("start" in versions[version].keys()):
                versionStart = versions[version]["start"]
                package["extras"].append({"key": "issued", "value": versionStart})
            if("end" in versions[version].keys()):
                versionEnd = versions[version]["end"]
                package["extras"].append({"key": "modified", "value": versionEnd})
            
        # Check if the dataset has to be updated
        checkPackage(CKAN, CKAN_URL, CKAN_KEY, datasets, package)

    # Delete the package at every iteration 
    del package


# Procedure to check the package to update for LiveSchema
def checkPackage(CKAN, CKAN_URL, CKAN_KEY, datasets, package):
    print(package["name"])

    # Check if the package is already on LiveSchema
    if package["name"] in datasets:
        # If the package is on LiveSchema then get the online version
        CKANpackage = CKAN.call_action('package_show', {"id": package["name"]})

        # Boolean used to verify if the online version is outdated
        a = False

        # Iterate over every combination of fields
        for CKANfield in CKANpackage.keys():
            for field in package.keys():
                # If the online version has different values on the fields (except the extras and tags) then update them and set it as outdated
                if(not a and CKANfield == field and CKANpackage[CKANfield] != package[field] and field != "extras" and field != "tags"):
                    CKANpackage[CKANfield] = package[field]
                    a = True
                    break

        # If there are different numbers of extra fields
        if(len(CKANpackage["extras"])!= len(package["extras"])):
            # Then the online version is outdated
            a = True

        # Iterate over every combination of extra fields
        for CKANextra in CKANpackage["extras"]:
            for extra in package["extras"]:
                # If the online version has different values on the extra fields then update them and set it as outdated
                if(not a and CKANextra["key"] == extra["key"] and CKANextra["value"] != extra["value"]):
                    CKANextra["value"] = extra["value"]
                    a = True
                    break

        # If the online version is outdated
        if(a):
            # Update the online version of the package
            CKAN.call_action("package_update", CKANpackage)
            log(json.dumps(CKANpackage))
            # Also if the package has a different url link
            if(CKANpackage["url"] != package["url"]):
                # Update its resources
                addResources(CKAN, CKAN_URL, CKAN_KEY, package, "update")
    else:
        # Create the package on LiveSchema
        log(json.dumps(package))
        CKAN.call_action("package_create", package)
        # Also create its resources
        addResources(CKAN, CKAN_URL, CKAN_KEY, package, "create")
    
    log("")


# Procedure to add the resources of the given package
def addResources(CKAN, CKAN_URL, CKAN_KEY, package, action):
    # Try to create the graph to analyze the vocabulary
    try:
        g = Graph()
        format_ = package["url"].split(".")[-1]
        if(format_ == "txt"):
            format_ = package["url"].split(".")[-2]
        format_ = format_.split("?")[0]
        result = g.parse(package["url"], format=guess_format(format_), publicID=package["name"])
    except Exception as e:
        # In case of an error during the graph's initiation, print the error and return an empty list
        print(str(e) + "\n")    
        return 

    try:
        # Serialize the vocabulary in n3
        g.serialize(destination=str(os.path.join("/tmp/", package["name"] + ".n3")), format="n3")
        # Add the serialized n3 file to LiveSchema
        requests.post(CKAN_URL+"/api/3/action/resource_"+action,
                data={"package_id":package["name"], "format": "n3", "name": package["name"]+".n3"},
                headers={"X-CKAN-API-Key": CKAN_KEY},
                files=[("upload", file("/tmp/"+package["name"]+".n3"))])
        # Remove the temporary n3 file from the server
        os.remove("/tmp/"+package["name"]+".n3")
    except Exception as e:
        # In case of an error during the graph's serialization, print the error
        print(str(e) + "\n")

    
    try:
        # Serialize the vocabulary in rdf
        g.serialize(destination=str(os.path.join("/tmp/", package["name"] + ".rdf")), format="pretty-xml")
        # Add the serialized rdf file to LiveSchema     
        requests.post(CKAN_URL+"/api/3/action/resource_"+action,
                    data={"package_id":package["name"], "format": "rdf", "name": package["name"]+".rdf"},
                    headers={"X-CKAN-API-Key": CKAN_KEY},
                    files=[("upload", file("/tmp/"+package["name"]+".rdf"))])
        # Remove the temporary rdf file from the server
        os.remove("/tmp/"+package["name"]+".rdf")
    except Exception as e:
        # In case of an error during the graph's serialization, print the error
        print(str(e) + "\n")


    list_ = list()
    # For each statement present in the graph obtained store the triples
    index = 0
    for subject, predicate, object_ in g:
        # Compute the filtered statement of the Triples
        subjectTerm = subject.replace("/", "#").split("#")[-1]
        if(not len(subjectTerm) and len(subject.replace("/", "#").split("#")) > 1):
            subjectTerm = subject.replace("/", "#").split("#")[-2]
        predicateTerm = predicate.replace("/", "#").split("#")[-1]
        if(not len(predicateTerm) and len(predicate.replace("/", "#").split("#")) > 1):
            predicateTerm = predicate.replace("/", "#").split("#")[-2]
        objectTerm = object_.replace("/", "#").split("#")[-1]
        if(not len(objectTerm) and len(object_.replace("/", "#").split("#")) > 1):
            objectTerm = object_.replace("/", "#").split("#")[-2]
        if(package["name"] == "freebase"):
            subjectTerm = subjectTerm.split(".")[-1]
            if(not len(subjectTerm) and len(subjectTerm.split(".")) > 1):
                subjectTerm = subjectTerm.split(".")[-2]
            predicateTerm = predicateTerm.split(".")[-1]
            if(not len(objectTerm) and len(predicateTerm.split(".")) > 1):
                predicateTerm = predicateTerm.split(".")[-2]
            objectTerm = objectTerm.split(".")[-1]
            if(not len(objectTerm) and len(objectTerm.split(".")) > 1):
                objectTerm = objectTerm.split(".")[-2]

        
        # Save the statement to the List to be added to the DataFrame
        list_.insert(index,{"Subject": subject, "Predicate": predicate, "Object": object_, "SubjectTerm": subjectTerm, "PredicateTerm": predicateTerm, "ObjectTerm": objectTerm, "Domain": package["name"], "Domain Version": package["version"]})
        index += 1
    
    # Create the DataFrame to save the vocabs' information
    DTF = pd.DataFrame(list_, columns=["Subject", "Predicate", "Object", "SubjectTerm", "PredicateTerm", "ObjectTerm", "Domain", "Domain Version"])
    # Parse the DataFrame into the csv file
    DTF.to_csv(os.path.normpath(os.path.expanduser("/tmp/" + package["name"] + ".csv")))

    # Upload the csv file to LiveSchema
    requests.post(CKAN_URL+"/api/3/action/resource_"+action,
                data={"package_id":package["name"], "format": "csv", "name": package["name"]+".csv"},
                headers={"X-CKAN-API-Key": CKAN_KEY},
                files=[("upload", file("/tmp/" + package["name"] + ".csv"))])

    # Remove the temporary csv file from the server
    os.remove("/tmp/" + package["name"] + ".csv")


# Logs the date with the string str to track errors 
def log(str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S - ", time.gmtime())
    f = open("log.txt", "a+")
    f.write(ts + str + "\n")
    f.close()

# Set the URL and admin key of LiveSchema
CKAN_URL = "http://streambase7.disi.unitn.it:5000/"
CKAN_KEY = "873daee2-3cd4-4621-9079-730f01609ce1"

# Create the CKAN Remote api caller
CKAN = ckanapi.RemoteCKAN(CKAN_URL,
    apikey= CKAN_KEY,
    user_agent="liveschema/1.0 (+http://liveschema.org/)")


# Get the list of catalogs and datasets to use to check the current state of LiveSchema
catalogs = CKAN.call_action('organization_list')
datasets = CKAN.call_action('package_list')


# Scrape the the Others excel file from github
scrapeOthers(CKAN, CKAN_URL, CKAN_KEY, catalogs, datasets)

# Scrape the LOV Repository
#scrapeLOV(CKAN, CKAN_URL, CKAN_KEY, catalogs, datasets)
