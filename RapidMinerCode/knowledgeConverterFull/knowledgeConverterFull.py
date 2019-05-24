#! /usr/bin/python3.6
# Import libraries
from rdflib import Graph, Literal, RDFS, RDF, OWL, Namespace, URIRef
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
def rm_main(data, orig, predicates = pd.DataFrame()):
    # Create the graph used to store the vocabulary
    g = Graph()
    # Create the Namespace for the vocabulary
    n = Namespace("http://www.liveschema.org/test/")
    g.bind("liveschema_test", n)
    
    # Create the DataFrame used to save the triples
    triples = pd.DataFrame(columns=["Subject","Predicate", "Object", "SubjectTerm","PredicateTerm", "ObjectTerm"])

    # Sets used to avoid adding 2 equal rows in the DataFrame
    nameSet = set()
    elementSet = set()

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
        for element in elements:
            # Save the triple about the element being an ObjectProperty
            triples = triples.append({"Subject": " "+str(n[element]), "Predicate": str(RDF.type), "Object": str(OWL.ObjectProperty), "SubjectTerm": element, "PredicateTerm": "type", "ObjectTerm": "ObjectProperty"}, ignore_index=True)
            g.add((n[element], RDF.type, OWL.ObjectProperty))
            # Save the triple about the element being a domain of that Names
            triples = triples.append({"Subject": " "+str(n[element]), "Predicate": str(RDFS.domain), "Object": " "+str(n[names]), "SubjectTerm": element, "PredicateTerm": "domain", "ObjectTerm": names}, ignore_index=True)
            g.add((n[element], RDFS.domain, n[names]))

        # Complete the file and excel with the original vocabulary
        # Iterate over every item of the original vocabulary
        for i, r in orig.iterrows():
            # Check if the triple has to be saved, if there is a predicate selection then checks if that predicate has to be saved
            bool_ = False
            # If there is no predicate selection then save every triple
            if(len(predicates) == 0):
                bool_ = True
            # If there is a predicate selection then check if that predicate has to be saved
            else:
                for pred in predicates[predicates.columns[0]]:
                    if(pred == str(r["PredicateTerm"]) or pred == str(r["Predicate"])):
                        bool_ = True
                        break
            # Check if the triple has to be saved
            if(bool_ == True):
                # Save the original name triples on the new graph
                for name in nameList:
                    nameSet.add(name+r["PredicateTerm"]+r["ObjectTerm"])
                    # If the name is an original subject then try to save it
                    if(name == r["SubjectTerm"]):
                        # Save the triple about the name being a SubjectTerm
                        triples = triples.append({"Subject": " "+str(n[name]), "Predicate": " "+str(n["isA"]), "Object": r["Subject"], "SubjectTerm": name, "PredicateTerm": "isA", "ObjectTerm": r["SubjectTerm"]}, ignore_index=True)
                        g.add((n[name], n["isA"], Literal(r["Subject"])))
                        # Save the triple about the name becoming the SubjectTerm in that triple
                        triples = triples.append({"Subject": " "+str(n[name]), "Predicate": r["Predicate"], "Object": r["Object"], "SubjectTerm": name, "PredicateTerm": r["PredicateTerm"], "ObjectTerm": r["ObjectTerm"]}, ignore_index=True)
                        g.add((n[name], URIRef(r["Predicate"]), Literal(r["Object"])))

                # Save the original element triples on the new graph
                for element in elements:
                    elementSet.add(element+r["PredicateTerm"]+r["ObjectTerm"])
                    # If the element is a part of the original then try to save it
                    if(element in r["SubjectTerm"].lower()):
                        term = r["SubjectTerm"]
                        a = len(term)
                        # Check on which word element is connected with SubjectTerm, and check that are the same words
                        for i in range(a-1, -1, -1):
                            if(term[i].isupper() or i == 0):
                                if(term[i:a].lower() == element):
                                    # Save the triple about the element being a SubjectTerm
                                    triples = triples.append({"Subject": " "+str(n[element]), "Predicate": " "+str(n["isA"]), "Object": r["Subject"], "SubjectTerm": element, "PredicateTerm": "isA", "ObjectTerm": r["SubjectTerm"]}, ignore_index=True)
                                    g.add((n[element], n["isA"], Literal(r["Subject"])))
                                    # Save the triple about the element becoming the SubjectTerm in that triple
                                    triples = triples.append({"Subject": " "+str(n[element]), "Predicate": r["Predicate"], "Object": r["Object"], "SubjectTerm": element, "PredicateTerm": r["PredicateTerm"], "ObjectTerm": r["ObjectTerm"]}, ignore_index=True)
                                    g.add((n[element], URIRef(r["Predicate"]), Literal(r["Object"])))
                                # Update the index
                                a = i            

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


from datetime import datetime


tick = datetime.now()

print("Cross...")
test = pd.read_excel(os.path.normpath(os.path.expanduser("~/Desktop/CIS_CrossData.xlsx")))
print("Inh...")
orig = pd.read_excel(os.path.normpath(os.path.expanduser("~/Desktop/Pars_CIS.xlsx")))
print("Pred...")
PrTest = pd.read_excel(os.path.normpath(os.path.expanduser("~/Desktop/Predicate.xlsx")))
print("RM...")
res = rm_main(test, orig, PrTest)
print("Conv...")
res.to_excel(os.path.normpath(os.path.expanduser("~/Desktop/CIS_Conv_C.xlsx")))

tock = datetime.now()   
diff = tock - tick    # the result is a datetime.timedelta object
print(str(diff.total_seconds()) + " seconds") 