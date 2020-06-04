# Import libraries
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import re
import json
import ckanapi


# Logs the date with the string str to track errors 
def log(str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S - ", time.gmtime())
    f = open("log.txt", "a+")
    f.write(ts + str + "\n")
    f.close()

# Set the URL and admin key of LiveSchema
CKAN_URL = "http://127.0.0.1:5000"
CKAN_KEY = "0587249a-c6e6-4b75-914a-075d88b16932"

# Create the CKAN Remote api caller
CKAN = ckanapi.RemoteCKAN(CKAN_URL,
    apikey= CKAN_KEY,
    user_agent="liveschema/1.0 (+http://liveschema.org/)")

#Clean the database of LiveSchema
def cleanCKAN(CKAN):
    ep = CKAN.call_action('package_list')
    for pack in ep:
        try:
            log("Removed dataset "+pack+"\n")
            print("Removed dataset "+pack)
            CKAN.call_action('dataset_purge', {"id": pack, "force":"True"})
        except:
            log("Exception")
            print("Exception")


    eo = CKAN.call_action('organization_list')
    for org in eo:
        try:
            log("Removed organization "+org+"\n")
            print("Removed organization "+org)
            CKAN.call_action('organization_purge', {"id": org, "force":"True"})
        except:
            log("Exception")
            print("Exception")

    eg = CKAN.call_action('group_list')
    for group in eg:
        try:
            log("Removed group "+group+"\n")
            print("Removed group "+group)
            CKAN.call_action('group_purge', {"id": group, "force":"True"})
        except:
            log("Exception")
            print("Exception")


cleanCKAN(CKAN)

# Clear Job List of all queues
#CKAN.call_action('job_clear', {})

#CKAN.call_action('group_purge', {"id": "biswanath-dutta", "force":"True"})
#CKAN.call_action("group_create", {"name": "biswanath-dutta", "title": "Biswanath Dutta", "extras": [{"key": "URI", "value": "https://sites.google.com/site/dutta2005/home"}]})
     
