# Import libraries
import rdflib
from rdflib import URIRef, Graph, Namespace
from rdflib.util import guess_format
from rdflib.plugins.parsers.notation3 import N3Parser
from pathlib import Path
import pandas as pd
import os
import time
import re

# Parse the given file and add its information to the file Excel given as third parameter
def parse(dir, dirName, file, df, originDir):
    root = os.path.join(dir, dirName) 
    # Create a graph to analyze the n3 file
    g = Graph()
    try:
        fileObj = open(os.path.join(root, file), "r",encoding="utf8")
        result = g.parse(file=fileObj, format=guess_format(file))
        fileObj.close()
        log("Parsed " + file + "\n")
    except Exception as e:
        log("Error trying to parse " + file + "\n")
        log(str(e) + "\n")

    # For each statement present in the graph obtained
    for subject, predicate, object_ in g:
        # Save the statement to the ExcelFile
        domain = file.replace("_", ".").split(".")[0]
        df = df.append({'Subject': subject, 'Predicate': predicate, 'Object': object_, 'Domain': domain}, ignore_index=True)
    return df

# Logs the date with the string str to track errors 
def log(str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S - ", time.gmtime())
    f = open("log.txt", "a+")
    f.write(ts + str)
    f.close()

def rm_main():
    # Extract the directory path to where to find the vocabs
    originDir = os.path.dirname(os.path.abspath(__file__))
    dir = os.path.join("C:\\Users\\marco\\Desktop\\Internship" , "Resources")

    df = pd.DataFrame(columns=['Subject', 'Predicate', 'Object', 'Domain'])

    # Iterate for every directory
    for dirName in os.listdir(dir):
        # For each directory create a new ExcelFile
        if(os.path.isdir(os.path.join(dir, dirName))):
            # Add information for each file of the directory
            for fileName in os.listdir(os.path.join(dir, dirName)):
                df = parse(dir, dirName, fileName, df, originDir)

    df.to_csv("vocabs.csv")

    return df

rm_main()