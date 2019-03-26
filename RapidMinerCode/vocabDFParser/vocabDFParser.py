# Import libraries
import rdflib
from rdflib import URIRef, Graph, Namespace
from rdflib.util import guess_format
from rdflib.plugins.parsers.notation3 import N3Parser
from pathlib import Path
import pandas as pd
import time

# Parse the given file and add its information to the file Excel given as third parameter
def parse(name, link, file, df):
    # Create a graph to analyze the n3 file
    g = Graph()
    try:
        log("Parsing: " + name + "\n")
        result = g.parse(link, format=guess_format(name.split("/")[-1]))
        log("Parsed : " + name + "\n")
    except Exception as e:
        log("Error trying to parse " + name + "\n")
        log(str(e) + "\n")
        return df

    # For each statement present in the graph obtained
    for subject, predicate, object_ in g:
        # Save the statement to the ExcelFile
        # Save the statement to the ExcelFile
        predicateTerm = predicate.replace("/", "#").split("#")
        predicateTerm = predicateTerm[len(predicateTerm)-1]
        objectTerm = object_.replace("/", "#").split("#")
        objectTerm = objectTerm[len(objectTerm)-1]
        domain = name.replace("_", ".").split(".")[0]
        df = df.append({"Subject": subject, "Predicate": predicateTerm, "Object": objectTerm, "Domain": domain}, ignore_index=True)
    return df

# Logs the date with the string str to track errors 
def log(str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S - ", time.gmtime())
    f = open("log.txt", "a+")
    f.write(ts + str)
    f.close()

def rm_main(vocabs):
    # Create the DataFrame to save the vocabs' Subject, Predicate, Object, and Domain
    df = pd.DataFrame(columns=["Subject", "Predicate", "Object", "Domain"])

    i = 0
    # Iterate for every row of the DataFrame
    for index, row in vocabs.iterrows():
        df = parse(row["Name"], row["Link"], row["File"], df)
        if(i == 20):
            break
        i+=1

    df.to_csv("vocabs.csv")
    df.to_excel("vocabs.xlsx", sheet_name = "Data")

    return df


# Extract the directory path to where to find the vocabs
rm_main(pd.read_csv("C:\\Users\\marco\\Desktop\\Internship\\RapidMinerCode\\LOVScraper\\LOVvocabs.csv"))