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
    e = CKAN.call_action('package_list')
    for pack in e:
        log("Removed dataset "+pack+"\n")
        CKAN.call_action('dataset_purge', {"id": pack, "force":"True"})

    e = CKAN.call_action('organization_list')
    for org in e:
        log("Removed organization "+org+"\n")
        CKAN.call_action('organization_purge', {"id": org, "force":"True"})

#cleanCKAN(CKAN)
CKAN.call_action('organization_purge', {"id": "lov", "force":"True"})