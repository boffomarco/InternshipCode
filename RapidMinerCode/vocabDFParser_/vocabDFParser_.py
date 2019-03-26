# Import libraries
import rdflib
from rdflib import URIRef, Graph, Namespace
from rdflib.util import guess_format
from rdflib.plugins.parsers.notation3 import N3Parser
from pathlib import Path
import pandas as pd
import time

# Parse the given file and add its information to the file Excel given as third parameter
def parse(name, link, list_):
    # Create a graph to analyze the n3 file
    g = Graph()
    try:
        format_ = link.split(".")[-1]
        if(format_ == "txt"):
            format_ = link.split(".")[-2]
        format_ = format_.split("?")[0]
        log("Parsing: " + name + format_ + "\n")
        result = g.parse(link, format=guess_format(name+"."+"n3"))
        log("Parsed : " + name + "\n")
    except Exception as e:
        log("Error trying to parse " + name + "\n")
        log(str(e) + "\n")
        return list_, 0
    index = 0
    # For each statement present in the graph obtained
    for subject, predicate, object_ in g:
        # Save the statement to the ExcelFile
        # Save the statement to the ExcelFile
        predicateTerm = predicate.replace("/", "#").split("#")
        predicateTerm = predicateTerm[len(predicateTerm)-1]
        objectTerm = object_.replace("/", "#").split("#")
        objectTerm = objectTerm[len(objectTerm)-1]
        domain = name.replace("_", ".").split(".")[0]
        list_.insert(index,{"Subject": subject, "Predicate": predicateTerm, "Object": objectTerm, "Domain": domain})
        index += 1
    return list_, index

# Logs the date with the string str to track errors 
def log(str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S - ", time.gmtime())
    f = open("log.txt", "a+")
    f.write(ts + str)
    f.close()

def rm_main(otherVocabs):
    # Create the DataFrame to save the vocabs' Subject, Predicate, Object, and Domain
    df = pd.DataFrame(columns=["Subject", "Predicate", "Object", "Domain"])

    
    if(len(otherVocabs)):
        # Iterate for every row of the DataFrame
        for index, row in otherVocabs.iterrows():
            print(row["Name"], row["Link"])
            list_, i = parse(row["Name"], row["Link"], list())
            if(i and len(list_)):
                df = df.append(list_)

    df.to_csv("vocabs.csv")

    return df


# Extract the directory path to where to find the vocabs
rm_main( pd.read_excel("C:\\Users\\marco\\Desktop\\Internship\\RapidMiner\\Data\\otherVocabs.xlsx"))