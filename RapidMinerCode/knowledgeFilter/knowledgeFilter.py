import pandas as pd

# Mandatory function for RapidMiner
def rm_main(predicates, triples):    
    # Create the DataFrame to save the vocabs' triples with the predicates present on the argument 'predicates'
    df = pd.DataFrame(columns=["Type", "Property"])

    # Iterate for every predicate present on 'predicates'
    for ind_, r in predicates.iterrows():
        # Create the list used to add the triples that has that predicate
        list_ = list()
        index_ = 0
        # Iterate for every triples present on the file passed on the argument 'triples'
        for index, row in triples.iterrows():
            # if a triple has a specified Predicate
            if(row["Predicate"] in r["Predicate"]):
                # Save that triple on the list
                list_.insert(index_,{"Type": row["Object"], "Property": row["Subject"]})
                index_ += 1
        # Save the information on the list to the DataFrame for each predicate checked
        if(index_ and len(list_)):
            df = df.append(list_)
    # Return the DataFrame for RapidMiner usage
    return df

import os
import time
import re

# Create the folder used to store the results
location = os.path.normpath(os.path.expanduser("~/Desktop/K-Files/"))

# Create the DataFrame to save the vocabs' Date of parsing, Subject, Predicate, Object, Domain, Domain Version, Domain Date, URI, Title, Languages
DataF = pd.DataFrame(columns=["Type", "Property"])

# Add information for each file of the directory
for fileName in os.listdir(location):
    if("_Filtered_" in fileName):    
        ts = time.strftime("%Y-%m-%d %H:%M:%S - ", time.gmtime())
        print(ts+" Inizio  "+fileName)
        returnedDF = rm_main(pd.read_excel(r"C:\Users\marco\Desktop\Internship\RapidMinerCode\knowledgeFilter\Predicate.xlsx"), pd.read_excel(os.path.join(location,fileName)))
        ts = time.strftime("%Y-%m-%d %H:%M:%S - ", time.gmtime())
        print(ts+" Salva   "+fileName)
        # Save the information on the DataFrame for each vocabulary
        n=len(returnedDF)
        ts = time.strftime("%Y-%m-%d %H:%M:%S - ", time.gmtime())
        print(ts+" Numero  "+str(n))
        if(n):
            DataF = DataF.append(returnedDF, ignore_index = True)
            ts = time.strftime("%Y-%m-%d %H:%M:%S - ", time.gmtime())
            print(ts+" NumeroT "+str(len(DataF)))

DataF.to_excel(r"C:\Users\marco\Desktop\Internship\RapidMinerCode\knowledgeFilter\Sol.xlsx")
