# Import libraries
from rdflib import Graph, Literal, RDFS, Namespace
import pandas as pd
import os

# Mandatory function for RapidMiner
def rm_main(data):
    # Create the graph used to store the vocabulary
    g = Graph()
    # Create the Namespace for the vocabulary
    n = Namespace("http://www.liveschema.org/test/")
    g.bind("liveschema_test", n)
    
    # Sort the DataFrame
    data = data.sort_values("total")
    # Iterate for every row present on data
    for index_, row in data.iterrows():
        # Get the names of the domains and saves them using subClassOf and label
        names = row["Names"].replace(" ","").replace("[","").replace("]","").replace("'","").replace(",", "_-_")
        nameList = names.split("_-_")
        print(names)
        for name in nameList:
            g.add((n[names], RDFS.label, Literal(name)))
            if(name != names):
                g.add((n[name], RDFS.subClassOf, n[names]))

        # Map every element into its domain
        elements = row["Elements"].replace(" ","").replace("[","").replace("]","").replace("'","").split(",")
        print(elements)
        for element in elements:
            g.add((n[element], RDFS.domain, n[names]))

    # Create the directory in which store the new vocabulary
    location = os.path.normpath(os.path.expanduser("~/Desktop/K-Files/Converted/"))
    if not os.path.isdir(location):
        os.makedirs(location)
    # Serialize the new vocabulary
    g.serialize(destination=str(os.path.join(location, "test.rdf")), format="pretty-xml")
    g.serialize(destination=str(os.path.join(location, "test.n3")), format="n3")
    g.serialize(destination=str(os.path.join(location, "test.nt")), format="nt")
    g.serialize(destination=str(os.path.join(location, "test.ttl")), format="turtle")
    g.serialize(destination=str(os.path.join(location, "test.json-ld")), format="json-ld")  

test = pd.read_excel(os.path.normpath(os.path.expanduser("~/Desktop/analysis-step/CrossData.xlsx")))
#print(test)
rm_main(test)