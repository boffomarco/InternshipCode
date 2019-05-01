# Import libraries
import pandas as pd

# Mandatory function for RapidMiner
def rm_main(triples, predicates = pd.DataFrame()):    
    # Create the DataFrame to save the vocabs' triples with the predicates present on the argument 'predicates'
    df = pd.DataFrame(columns=["Type", "Property"])

    # Return all the triples if there is no predicate filtering
    if((len(predicates) == 0)):
        df["Type"] = triples["ObjectTerm"]
        df["Property"] = triples["SubjectTerm"]
        return df

    # Iterate for every predicate present on 'predicates'
    for ind_, r in predicates.iterrows():
        # Create the list used to add the triples that has that predicate
        list_ = list()
        index_ = 0
        # Iterate for every triples present on the file passed on the argument 'triples'
        for index, row in triples.iterrows():
            # if a triple has a specified PredicateTerm or the predicates are not set
            if((str(row["PredicateTerm"]) == str(r[data.columns[0]]))):
                # Save that triple on the list
                list_.insert(index_,{"Type": row["ObjectTerm"], "Property": row["SubjectTerm"]})
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
location = os.path.normpath(os.path.expanduser("~/Desktop/K-Files/IN/"))

# Create the DataFrame to save the vocab
DataF = pd.DataFrame(columns=["Type", "Property"])

# Add information for each file of the directory
for fileName in os.listdir(location):
    print(fileName)    
    ts = time.strftime("%Y-%m-%d %H:%M:%S - ", time.gmtime())
    print(ts+" Inizio  "+fileName)
    returnedDF = rm_main(pd.read_excel(os.path.join(location,fileName)) )#, pd.read_excel(r"C:\Users\marco\Desktop\Internship\InternshipCode\RapidMinerCode\knowledgeFilter\Predicate.xlsx"))
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

DataF.to_excel(r"C:\Users\marco\Desktop\Sol.xlsx")
