# Import libraries
import pandas as pd

# Mandatory function for RapidMiner
def rm_main():
    # Create the DataFrame to save the LOVs' vocabs' information
    df = pd.DataFrame(columns=["prefix", "URI", "Title", "Languages", "VersionName", "VersionDate", "Link", "Folder"])
    
    # Get the other vocabularies from the Excel file from github
    vocabs = pd.read_excel("https://raw.githubusercontent.com/knowdive/resources/master/otherVocabs.xlsx")
    # Create the list used to contain the information about the other vocabularies
    list_ = list()
    index = 0
    # Iterate for every vocabulary read from the Excel file
    for index, row in vocabs.iterrows():
        # Add the vocabulary to the list
        list_.insert(index,{"prefix": row["prefix"], "URI": row["URI"], "Title": row["Title"], "Languages": row["Languages"], "VersionName": row["VersionName"], "VersionDate": row["VersionDate"], "Link": row["Link"], "Folder": row["Folder"]})
        # Update the index for the next element of the list
        index += 1
    # Add the list of that Excel file to the DataFrame, if there are vocabularies in that Excel file
    if(len(list_)):
        df = df.append(list_, ignore_index=True)
    
    # Return the DataFrame for RapidMiner visualization
    return df

print(rm_main())