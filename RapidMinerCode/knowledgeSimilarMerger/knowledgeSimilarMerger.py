#! /usr/bin/python3.6
# Import libraries
import pandas as pd
from collections import defaultdict
from rdflib import Graph, Literal, RDFS, RDF, OWL, Namespace, URIRef
import os

# Mandatory function for RapidMiner
def rm_main(triples, similarities):
    # Create the defaultdict used to store the combination of ObjectTerm and SubjectTerms
    comb = set()
    # Iterate over every triples row
    for index, row in similarities.iterrows():
        if("in class" in row["FIRST_ID"] and "in class" in row["SECOND_ID"] and row["DISTANCE"] > 5):
            # Set a boolean to know if that combination is already in the defaultdict
            b = False
            # Iterate over every key of the defaultdict
            for key in comb:
                # Create a list of the keys for every key of the defaultdict
                keys = key.split()
                # If both the typeTerms are in the keys then there is nothing to add
                if(row["FIRST_ID"][10:-1] in keys and row["SECOND_ID"][10:-1] in keys):
                    # Set the boolean to True and exit the for cycle since the combination is in the defaultdict
                    b=True
                    break
                # If a typeTerm is already in the defaultdict and the other typeTerm is not, add the other typeTerm to the combination of the first typeTerm in the defaultdict
                if(not b and row["FIRST_ID"][10:-1] in keys and row["SECOND_ID"][10:-1] not in keys):
                    # Delete the old combination
                    comb.remove(key)
                    # Generate the new key for the combination adding the new typeTerm
                    key = key + " " + row["SECOND_ID"][10:-1]
                    # Update the defaultdict with the new combination
                    comb.add(key)
                    # Set the boolean to True and exit the for cycle since the combination is in the defaultdict now
                    b=True
                    break
                # If a typeTerm is already in the defaultdict and the other typeTerm is not, add the other typeTerm to the combination of the first typeTerm in the defaultdict
                if(not b and row["SECOND_ID"][10:-1] in keys and row["FIRST_ID"][10:-1] not in keys):
                    # Delete the old combination
                    comb.remove(key)
                    # Generate the new key for the combination adding the new typeTerm
                    key = key + " " + row["FIRST_ID"][10:-1]
                    # Update the defaultdict with the new combination
                    comb.add(key)
                    # Set the boolean to True and exit the for cycle since the combination is in the defaultdict now
                    b=True
                    break

            # If the combination is not in the defaultdict
            if(not b):
                # Add the combination to the defaultdict
                comb.add(row["FIRST_ID"][10:-1]+" "+row["SECOND_ID"][10:-1])
    
    # Create the graph used to store the vocabulary
    g = Graph()
    # Create the Namespace for the vocabulary
    n = Namespace("http://liveschema.org/Similarity_Merge/")
    g.bind("liveschema_similarity_merge", n)

    # Create the DataFrame to save the vocabs' Date of parsing, Subject, Predicate, Object, Domain, Domain Version, Domain Date, URI, Title, Languages
    newTriples = pd.DataFrame(columns=["Date", "Subject", "Predicate", "Object", "SubjectTerm", "PredicateTerm", "ObjectTerm", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"])
    
    # Iterate over every triples row
    for index, row in triples.iterrows():
        # Boolean used to identify if the row has been added as jaccard value
        jBool = True
        # Iterate over every jaccard combination of 
        for key in comb:
            if(jBool and row["ObjectTerm"] in key.split()):
                objTerms = "_-_".join(key.split())
                # Save the triple
                newTriples = newTriples.append({"Date": row["Date"], "Subject": row["Subject"], "Predicate": row["Predicate"], "Object": n[objTerms], "SubjectTerm": row["SubjectTerm"], "PredicateTerm": row["PredicateTerm"], "ObjectTerm": objTerms, "Domain": row["Domain"], "Domain Version": row["Domain Version"], "Domain Date": row["Domain Date"], "URI": row["URI"], "Title": row["Title"], "Languages": row["Languages"]}, ignore_index=True)
                g.add((URIRef(row["Subject"]), URIRef(row["Predicate"]), n[objTerms]))
                jBool = False
            if(jBool and row["SubjectTerm"] in key.split()):
                subjTerms = "_-_".join(key.split())
                # Save the triple
                newTriples = newTriples.append({"Date": row["Date"], "Subject": n[subjTerms], "Predicate": row["Predicate"], "Object": row["Object"], "SubjectTerm": subjTerms, "PredicateTerm": row["PredicateTerm"], "ObjectTerm": row["ObjectTerm"], "Domain": row["Domain"], "Domain Version": row["Domain Version"], "Domain Date": row["Domain Date"], "URI": row["URI"], "Title": row["Title"], "Languages": row["Languages"]}, ignore_index=True)
                # Add the triple to the graph as URIRef or Literal respectively
                if(len(str(row["Object"])) > 5 and "http" == row["Object"][0:3]):
                    g.add((n[subjTerms], URIRef(row["Predicate"]), URIRef(row["Object"])))
                else:
                    g.add((n[subjTerms], URIRef(row["Predicate"]), Literal(row["Object"])))
                jBool = False
        if(jBool):
            # Save the triple
            newTriples = newTriples.append({"Date": row["Date"], "Subject": row["Subject"], "Predicate": row["Predicate"], "Object": row["Object"], "SubjectTerm": row["SubjectTerm"], "PredicateTerm": row["PredicateTerm"], "ObjectTerm": row["ObjectTerm"], "Domain": row["Domain"], "Domain Version": row["Domain Version"], "Domain Date": row["Domain Date"], "URI": row["URI"], "Title": row["Title"], "Languages": row["Languages"]}, ignore_index=True)
            # Add the triple to the graph as URIRef or Literal respectively
            if(len(row["Object"]) > 5 and "http" == row["Object"][0:3]):
                g.add((URIRef(row["Subject"]), URIRef(row["Predicate"]), URIRef(row["Object"])))
            else:
                g.add((URIRef(row["Subject"]), URIRef(row["Predicate"]), Literal(row["Object"])))
    
    # Create the directory in which store the new vocabulary
    mergedFileDestination = "~/Desktop/K-Files/Converted/testConverted.ttl"
    location = os.path.normpath(os.path.expanduser("/".join(mergedFileDestination.split("/")[0:-1])))
    if not os.path.isdir(location):
        os.makedirs(location)
    # Serialize the new vocabulary
    if("rdf" in mergedFileDestination.split(".")[-1]):
        g.serialize(destination=str(os.path.join(location, mergedFileDestination.split("/")[-1])), format="pretty-xml")
    if("n3" in mergedFileDestination.split(".")[-1]):
        g.serialize(destination=str(os.path.join(location, mergedFileDestination.split("/")[-1])), format="n3")
    if("nt" in mergedFileDestination.split(".")[-1]):
        g.serialize(destination=str(os.path.join(location, mergedFileDestination.split("/")[-1])), format="nt")
    if("ttl" in mergedFileDestination.split(".")[-1]):
        g.serialize(destination=str(os.path.join(location, mergedFileDestination.split("/")[-1])), format="turtle")
    if("json" in mergedFileDestination.split(".")[-1]):
        g.serialize(destination=str(os.path.join(location, mergedFileDestination.split("/")[-1])), format="json-ld")
    
    # Return the DataFrame for RapidMiner usage
    return newTriples


from datetime import datetime

tick_ = datetime.now()
tick = datetime.now()

print("Inh...")
orig = pd.read_excel(os.path.normpath(os.path.expanduser("~/Desktop/Pars_OWL.xlsx")))
sim = pd.read_excel(os.path.normpath(os.path.expanduser("~/Desktop/Similarity.xlsx")))

tock = datetime.now()   
diff = tock - tick    # the result is a datetime.timedelta object
print(str(diff.total_seconds()) + " seconds") 
tick = datetime.now()

print("RM...")
new = rm_main(orig, sim)

tock = datetime.now()   
diff = tock - tick    # the result is a datetime.timedelta object
print(str(diff.total_seconds()) + " seconds") 
tick = datetime.now()

print("Conv...")
new.to_excel(os.path.normpath(os.path.expanduser("~/Desktop/OWL_NEW_S.xlsx")))

tock = datetime.now()   
diff = tock - tick    # the result is a datetime.timedelta object
print(str(diff.total_seconds()) + " seconds") 

diff = tock - tick_    # the result is a datetime.timedelta object
print(str(diff.total_seconds()) + " seconds") 