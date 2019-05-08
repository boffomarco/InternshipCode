# Import libraries
from rdflib import Graph, Literal, RDFS, RDF, OWL, Namespace
import pandas as pd
import os

# Check if subj is a subClassOf names
def check(subj, names):
    s_ = subj.split("_-_")
    n_ = names.split("_-_")
    i = 0
    for su in s_:
        for na in n_:
            if(na == su):
                i+=1
    return (i == len(s_))

# Mandatory function for RapidMiner
def rm_main(data):
    # Create the graph used to store the vocabulary
    g = Graph()
    # Create the Namespace for the vocabulary
    n = Namespace("http://www.liveschema.org/test/")
    g.bind("liveschema_test", n)
    
    # Create the DataFrame used to save the triples
    triples = pd.DataFrame(columns=["Subject","Predicate", "Object"])

    subjects = set()
    # Sort the DataFrame
    data = data.sort_values("total")
    # Iterate for every row present on data
    for index_, row in data.iterrows():
        # Get the names of the domains and saves them using subClassOf and label
        names = row["Names"].replace(" ","").replace("[","").replace("]","").replace("'","").replace(",", "_-_")
        nameList = names.split("_-_")
        if(len(subjects)):
            for subj in subjects:
                if(check(subj, names)):
                    # Save the triple
                    triples = triples.append({"Subject": subj, "Predicate": "subClassOf", "Object": names}, ignore_index=True)
                    g.add((n[subj], RDFS.subClassOf, n[names]))
        if(len(nameList) > 1):
            subjects.add(names)
        
        #print(names)
        for name in nameList:
            # Save the triple
            triples = triples.append({"Subject": names, "Predicate": "comment", "Object": name}, ignore_index=True)
            g.add((n[names], RDFS.comment, Literal(name)))
            
            #print(name)
            if(name != names):
                # Save the triple
                triples = triples.append({"Subject": name, "Predicate": "subClassOf", "Object": names}, ignore_index=True)
                g.add((n[name], RDFS.subClassOf, n[names]))

        # Map every element into its domain
        elements = row["Elements"].replace(" ","").replace("[","").replace("]","").replace("'","").split(",")
        #print(elements)
        for element in elements:
            # Save the triple
            triples = triples.append({"Subject": element, "Predicate": "type", "Object": "ObjectProperty"}, ignore_index=True)
            g.add((n[element], RDF.type, OWL.ObjectProperty))
            # Save the triple
            triples = triples.append({"Subject": element, "Predicate": "domain", "Object": names}, ignore_index=True)
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

    # Return the triples DataFrame for RapidMiner usage
    return triples

test = pd.read_excel(os.path.normpath(os.path.expanduser("~/Desktop/analysis-step/DBPedia_CrossData.xlsx")))
#print(test)
rm_main(test).to_excel(os.path.normpath(os.path.expanduser("~/Desktop/DBPedia_Conv_C.xlsx")))