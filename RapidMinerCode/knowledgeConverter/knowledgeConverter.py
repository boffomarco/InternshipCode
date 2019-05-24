#! /usr/bin/python3.6
# Import libraries
from rdflib import Graph, Literal, RDFS, RDF, OWL, Namespace
import pandas as pd
import os

# Check if rNames is a subClassOf Names
def checkSub(names, rNames, subsAdded, namesRemaining):
    bool_ = False
    # Split Names and rNames in the different name and rName of relative composition
    nameL = names.split("_-_")
    rNameL = rNames.split("_-_")
    # Count the number of rName found in rNames
    i = 0
    for name in nameL:
        for rName in rNameL:
            if(name == rName):
                i+=1
    # If the result of i is equal to the number of rName(all elements of rNames are on Names) and there isn't already a bigger subClass
    if(i==len(rNameL) and checkBiggerSub(rNameL, subsAdded)):
        # Set the boolean to true and add rNames as subClass of Names
        bool_ = True
        # Add rNames at the subClasses of Names
        subsAdded.add(rNames)
        # Remove the components of rNames from the components remaining
        for rName in rNameL:
            if(rName in namesRemaining):
                namesRemaining.remove(rName)
    # Return the bool and the modified sets
    return bool_, subsAdded, namesRemaining

# Check if subj is a subClassOf names
def checkBiggerSub(rNameL, subsAdded):
    # Iterate over every already added subClasses of Names
    for subj in subsAdded:
        # Count the number of rName found in subj
        i = 0
        for s in subj.split("_-_"):
            for rName in rNameL:
                if(s == rName):
                    i+=1
        # If the result of i is equal to the number of rName(all elements of rNames are on an already added subClass of Names)
        if(i == len(rNameL)):
            # Return False since a bigger subClass has already been added to Names
            return False
    # Return True since there aren't subClasses of Names that covers all these components of Names
    return True

# Mandatory function for RapidMiner
def rm_main(data):
    # Create the graph used to store the vocabulary
    g = Graph()
    # Create the Namespace for the vocabulary
    n = Namespace("http://www.liveschema.org/test/")
    g.bind("liveschema_test", n)
    
    # Create the DataFrame used to save the triples
    triples = pd.DataFrame(columns=["Subject","Predicate", "Object", "SubjectTerm","PredicateTerm", "ObjectTerm"])

    # Sort the DataFrame
    data = data.sort_values("total", ascending=False)
    # Iterate for every row present on data
    for index, row in data.iterrows():
        # Format Names
        names = row["Names"].replace(" ","").replace("[","").replace("]","").replace("'","").replace(",", "_-_")
        # Split Names in the different name of its composition
        nameList = names.split("_-_")
        # Comment the Names
        for name in nameList:
            # Save the triple about Names having as comments the various name of which it is composed
            triples = triples.append({"Subject": " "+str(n[names]), "Predicate": str(RDFS.comment), "Object": str(Literal(name)), "SubjectTerm": names, "PredicateTerm": "comment", "ObjectTerm": name}, ignore_index=True)
            g.add((n[names], RDFS.comment, Literal(name)))

        # Create set to contain the different subClasses of Names
        subsAdded = set()
        # Create set to contain the remaining single name of Names
        namesRemaining = set()
        namesRemaining.update(nameList)
        # Iterate over every item with less members in Names until all the name in Names has been covered
        for i, r in data.iterrows():
            # If Names in that row has less members than the starting Names, and not all the name in Names has been covered
            if(r["total"] < row["total"] and len(namesRemaining) != 0):
                # Format the new row Names: rNames
                rNames = r["Names"].replace(" ","").replace("[","").replace("]","").replace("'","").replace(",", "_-_")
                # Check if rNames can be a subClassOf Names
                bool_, subsAdded, namesRemaining = checkSub(names, rNames, subsAdded, namesRemaining)
                if(bool_):
                    # Save the triple about rNames being subClassOf Names
                    triples = triples.append({"Subject": " "+str(n[rNames]), "Predicate": str(RDFS.subClassOf), "Object": " "+str(n[names]), "SubjectTerm": rNames, "PredicateTerm": "subClassOf", "ObjectTerm": names}, ignore_index=True)
                    g.add((n[rNames], RDFS.subClassOf, n[names]))
        # If the its a composition of at least 2 name, then add the remaining name as subClassOf
        if(len(nameList)>1):
            # Iterate over any remaining name
            for sub in namesRemaining:
                # Save the triple about the single name being subClassOf Names
                triples = triples.append({"Subject": " "+str(n[sub]), "Predicate": str(RDFS.subClassOf), "Object": " "+str(n[names]), "SubjectTerm": sub, "PredicateTerm": "subClassOf", "ObjectTerm": names}, ignore_index=True)
                g.add((n[sub], RDFS.subClassOf, n[names]))

        # Map every element into its domain
        elements = row["Elements"].replace(" ","").replace("[","").replace("]","").replace("'","").split(",")
        #print(elements)
        for element in elements:
            # Save the triple about the element being an ObjectProperty
            triples = triples.append({"Subject": " "+str(n[element]), "Predicate": str(RDF.type), "Object": str(OWL.ObjectProperty), "SubjectTerm": element, "PredicateTerm": "type", "ObjectTerm": "ObjectProperty"}, ignore_index=True)
            g.add((n[element], RDF.type, OWL.ObjectProperty))
            # Save the triple about the element being a domain of that Names
            triples = triples.append({"Subject": " "+str(n[element]), "Predicate": str(RDFS.domain), "Object": " "+str(n[names]), "SubjectTerm": element, "PredicateTerm": "domain", "ObjectTerm": names}, ignore_index=True)
            g.add((n[element], RDFS.domain, n[names]))

    # Create the directory in which store the new vocabulary
    location = os.path.normpath(os.path.expanduser("~/Desktop/K-Files/Converted/"))
    if not os.path.isdir(location):
        os.makedirs(location)
    # Serialize the new vocabulary
    g.serialize(destination=str(os.path.join(location, "test.rdf")), format="pretty-xml")
    #g.serialize(destination=str(os.path.join(location, "test.n3")), format="n3")
    #g.serialize(destination=str(os.path.join(location, "test.nt")), format="nt")
    #g.serialize(destination=str(os.path.join(location, "test.ttl")), format="turtle")
    #g.serialize(destination=str(os.path.join(location, "test.json-ld")), format="json-ld")

    # Return the triples DataFrame for RapidMiner usage
    return triples

test = pd.read_excel(os.path.normpath(os.path.expanduser("~/Documents/Internship/analysis-step/CrossData.xlsx")))
#print(test)
rm_main(test).to_excel(os.path.normpath(os.path.expanduser("~/Desktop/OWL_Conv_C.xlsx")))