# Import libraries
import pandas as pd
from random import random

# Mandatory function for RapidMiner
def rm_main(triples):
    FolderPath = "/home/marco/Documents/Internship/resources/Vocabularies"
    DatasetName = "example"
    # Create output files
    train = open(FolderPath+"/"+DatasetName+"-train.txt", "w") 

    valid = open(FolderPath+"/"+DatasetName+"-valid.txt", "w") 

    test = open(FolderPath+"/"+DatasetName+"-test.txt", "w") 

    # Iterate over every triples row
    for index, row in triples.iterrows():
        # If the object value on the row has changed(first row or a new object)
        val = random()
        if(0 <= val < 0.7 ):
            train.write(row["SubjectTerm"]+"\t"+row["PredicateTerm"]+"\t"+row["ObjectTerm"]) 	
        elif( 0.7 < val < 0.9):
            valid.write(row["SubjectTerm"]+"\t"+row["PredicateTerm"]+"\t"+row["ObjectTerm"]) 
        elif(0.9 < val <= 1):
            test.write(row["SubjectTerm"]+"\t"+row["PredicateTerm"]+"\t"+row["ObjectTerm"]) 

    # Close Files
    train.close() 
    valid.close() 
    test.close() 

    return 


test = pd.read_csv(os.path.normpath(os.path.expanduser("~/Desktop/lov_mod.csv)))
#print(test)
rm_main(test)