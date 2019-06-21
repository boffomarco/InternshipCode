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

# Get the link of each dataset, parse it, then upload it