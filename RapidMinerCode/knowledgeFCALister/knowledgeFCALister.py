#! /usr/bin/python3.6
# Import libraries
import pandas as pd

# Mandatory function for RapidMiner
def rm_main(matrix):
    # Generate the resulting DataFrame having as words the tokenized columns of the matrix, and a total of 0 for every row
    data = pd.DataFrame({"word": matrix.columns[6:], "total": 0})

    # Sort the DataFrame on the new columns
    matrix = matrix.sort_values("TypeTerm")

    # Use a set to avoid creating duplicate Columns
    typeSet = set()
    # Iterate over every row of the matrix
    for index, row in matrix.iterrows():
        # Generate the name of the new column
        colName = "in class (" + row["TypeTerm"] + ")"
        # Check if that column is already present on the DataFrame
        typeSetL = len(typeSet)
        typeSet.add(row["TypeTerm"])
        # If there weren't columns with that name
        if(typeSetL < len(typeSet)):
            # Create a new column of 0 for that name
            data[colName] = 0

        # Iterate over overy tokenized column of the matrix
        i = 0
        for column in matrix.columns[6:]:
            # If the row has a value, then upload the values of the DataFrame
            if(row[column]):
                data.at[i, colName] = data.at[i, colName] + row[column]
                data.at[i, "total"] = data.at[i, "total"] + row[column]
            i+=1

    # Sort the DataFrame on the words
    data = data.sort_values("word")

    # Return the DataFrame for RapidMiner usage
    return data


import os
from datetime import datetime

tick_ = datetime.now()
tick = datetime.now()

print("Inh...")
orig = pd.read_excel(os.path.normpath(os.path.expanduser("~/Desktop/DBPedia_FCA.xlsx")))

tock = datetime.now()   
diff = tock - tick    # the result is a datetime.timedelta object
print(str(diff.total_seconds()) + " seconds") 
tick = datetime.now()

print("RM...")
res = rm_main(orig)

tock = datetime.now()   
diff = tock - tick    # the result is a datetime.timedelta object
print(str(diff.total_seconds()) + " seconds") 
tick = datetime.now()

print("Conv...")
res.to_excel(os.path.normpath(os.path.expanduser("~/Desktop/DBPedia_List.xlsx")))

tock = datetime.now()   
diff = tock - tick    # the result is a datetime.timedelta object
print(str(diff.total_seconds()) + " seconds") 

diff = tock - tick_    # the result is a datetime.timedelta object
print(str(diff.total_seconds()) + " seconds") 