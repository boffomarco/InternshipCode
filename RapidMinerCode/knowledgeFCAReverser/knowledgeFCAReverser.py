#! /usr/bin/python3.6
# Import libraries
from rdflib import Graph, Literal, RDFS, RDF, OWL, Namespace, URIRef
import pandas as pd
import os

# Mandatory function for RapidMiner
def rm_main(matrix):
    # Create the graph used to store the vocabulary
    g = Graph()
    # Create the Namespace for the vocabulary
    n = Namespace("http://www.liveschema.org/test/")
    g.bind("liveschema_test", n)
    
    # Create the DataFrame used to save the triples
    triples = pd.DataFrame(columns=["Subject","Predicate", "Object", "SubjectTerm","PredicateTerm", "ObjectTerm"], )

    # Iterate over all the rows of the matrix
    for index, row in matrix.iterrows():
        # Get the list of Properties of that row
        subjList = row["Properties"].split(" -")
        # Get the list of PropertiesTerms of that row
        subjTermList = row["PropertiesTerms"].split(" -")
        # Iterate over every Property
        for i in range(0, len(subjTermList)):
            # Save the triple about that Property being a domain of that row Type/Object
            triples = triples.append({"Subject": str(subjList[i]), "Predicate": str(RDFS.domain), "Object": str(row["Type"]), "SubjectTerm": subjTermList[i], "PredicateTerm": "domain", "ObjectTerm": row["TypeTerm"]}, ignore_index=True)
            g.add((URIRef(subjList[i].replace(" ", "")), RDFS.comment, URIRef(row["Type"].replace(" ", ""))))

    # Create the directory in which store the new vocabulary
    reversedFileDestination = "~/Desktop/K-Files/Converted/testConverted.ttl"
    location = os.path.normpath(os.path.expanduser("/".join(reversedFileDestination.split("/")[0:-1])))
    if not os.path.isdir(location):
        os.makedirs(location)
    # Serialize the new vocabulary
    if("rdf" in reversedFileDestination.split(".")[-1]):
        g.serialize(destination=str(os.path.join(location, reversedFileDestination.split("/")[-1])), format="pretty-xml")
    if("n3" in reversedFileDestination.split(".")[-1]):
        g.serialize(destination=str(os.path.join(location, reversedFileDestination.split("/")[-1])), format="n3")
    if("nt" in reversedFileDestination.split(".")[-1]):
        g.serialize(destination=str(os.path.join(location, reversedFileDestination.split("/")[-1])), format="nt")
    if("ttl" in reversedFileDestination.split(".")[-1]):
        g.serialize(destination=str(os.path.join(location, reversedFileDestination.split("/")[-1])), format="turtle")
    if("json" in reversedFileDestination.split(".")[-1]):
        g.serialize(destination=str(os.path.join(location, reversedFileDestination.split("/")[-1])), format="json-ld")

    # Return the triples DataFrame for RapidMiner usage
    return triples


from datetime import datetime

tick_ = datetime.now()
tick = datetime.now()

print("Inh...")
matrix = pd.read_excel(os.path.normpath(os.path.expanduser("~/Desktop/DBPedia_FCA.xlsx")))

tock = datetime.now()   
diff = tock - tick    # the result is a datetime.timedelta object
print(str(diff.total_seconds()) + " seconds") 
tick = datetime.now()

print("RM...")
res = rm_main(matrix)

tock = datetime.now()   
diff = tock - tick    # the result is a datetime.timedelta object
print(str(diff.total_seconds()) + " seconds") 
tick = datetime.now()

print("Conv...")
res.to_excel(os.path.normpath(os.path.expanduser("~/Desktop/DBPedia_Converted.xlsx")))

tock = datetime.now()   
diff = tock - tick    # the result is a datetime.timedelta object
print(str(diff.total_seconds()) + " seconds") 

diff = tock - tick_    # the result is a datetime.timedelta object
print(str(diff.total_seconds()) + " seconds") 