# Import libraries
import pandas as pd
import os

# Mandatory function for RapidMiner
def rm_main(data):
    # Drop the column 'in documents', that is equal to 'total'
    data.drop("in documents", axis=1, inplace=True)

    # Create the DataFrame used to save the Cues
    cue = pd.DataFrame(columns=["Class","Cue1", "Cue2", "Cue3", "Cue4", "Cue5", "Cue6"])
    # Iterate for every column present on data
    for column in data:
        # Rename the columns
        if "word" not in column:
            data.rename(index=str, columns={column: str(column+"_456")}, inplace= True)
            column += "_456"
        # Checks if the column identify a Class
        if("in class" in column):
            # Create the new column for the Cues in the input DataFrame, and calculate the values for every Element 
            index = data.columns.get_loc(column)
            className = "Cue(" + column[10:-5] + ")_456"
            tempColumn = data[column] / data["total_456"]
            data.insert(index, className, tempColumn)
            
            # Calculate the metrics of that Class
            cue4 = data[className].sum()
            cue5 = cue4 / data[column].sum()
            cue6 = 1 - cue5
            # Save the metrics of that Class
            cue.at[column[10:-5], 'Class'] = column[10:-5]
            cue.at[column[10:-5], 'Cue4'] = cue4
            cue.at[column[10:-5], 'Cue5'] = cue5
            cue.at[column[10:-5], 'Cue6'] = cue6

            # Create the new column for the Cues in the input DataFrame, and copy the values for every Element 
            index = data.columns.get_loc(column)
            className = column[0:-4] 
            tempColumn = data[column]
            data.insert(index, className + "_123", tempColumn)

    # Calculate the Knowledge metrics of the input
    cue4 = cue["Cue4"].sum()
    cue5 = cue4 / data["total_456"].sum()
    cue6 = 1 - cue5
    # Save the Knowledge metrics of the input
    cue.at["KNOWLEDGE", 'Class'] = "KNOWLEDGE"
    cue.at["KNOWLEDGE", 'Cue4'] = cue4
    cue.at["KNOWLEDGE", 'Cue5'] = cue5
    cue.at["KNOWLEDGE", 'Cue6'] = cue6

    # Create the new column for the Cues in the input DataFrame, and copy the values from the original column
    index = data.columns.get_loc("total_456")
    className = "total_123"
    tempColumn = data["total_456"]
    data.insert(index, className, tempColumn)

    # Create the DataFrame used to save the occurrences of the Names present on the Element row
    DF = pd.DataFrame(columns=["Element", "Names"])
    # Iterate for every row present on data, for every Element
    for index, row in data.iterrows():
        # Create a list to save the Names present on that row
        list_ = list()
        # For evert column that indicates a Name
        for column in data:
            # Check if the Name is present on that Element/row
            if(("in class" in column and "_456" in column) and row[column]): 
                # Save the Name on the list
                list_.append(column[10:-5])

                # Format data for another kind of cue Analysis
                if(row[column] > 1):
                    data.at[index, "total_123"] = row["total_123"] - row[column] + 1 
                    row["total_123"] = row["total_123"] - row[column] + 1
                    data.at[index, column[0:-4] + "_123" ] = 1
        # Save the correlation between Element and Names
        DF = DF.append({"Element": row["word"], "Names": list_}, ignore_index=True)

    # Create the DataFrame used to save the table used to identify common Elements between Names
    DTF = pd.DataFrame(columns=["total", "Names", "number", "Elements"])
    # Create the set used to check if new Names has to be added or if existing Names has to be updated
    set_ = set()
    # Iterate for every row present on DF, for every Element and the relative Names
    for index_, row in DF.iterrows():
        # Check if new Names has to be added or if existing Names has to be updated
        a = len(set_)
        set_.add(str(row["Names"]))
        if(a < len(set_)):
            # Create a new row on the DataFrame for that Names
            DTF.at[str(row["Names"]), "total"] = len(row["Names"])
            DTF.at[str(row["Names"]), "Names"] = row["Names"]
            DTF.at[str(row["Names"]), "Elements"] = str(row["Element"])
            DTF.at[str(row["Names"]), "number"] = 1
        else:
            # Update the row for that Names, adding the new Element
            elements = str(DTF.at[str(row["Names"]), "Elements"])
            number = DTF.at[str(row["Names"]), "number"]
            DTF.at[str(row["Names"]), "Elements"] = elements + " , " + str(row["Element"])
            DTF.at[str(row["Names"]), "number"] = number + 1

    # Iterate for every column present on data
    for column in data:
        # Checks if the column identify a Class
        if(("in class" in column and "_123" in column)):
            # Create the new column for the Cue in the input DataFrame, and calculate the values for every Element 
            index = data.columns.get_loc(column) - 1
            className = "Cue(" + column[10:-5] + ")_123"
            tempColumn = data[column] / data["total_123"]
            data.insert(index, className, tempColumn)
            
            # Calculate the metrics of that Class
            cue1 = data[className].sum()
            cue2 = cue1 / data[column].sum()
            cue3 = 1 - cue2
            # Save the metrics of that Class
            cue.at[column[10:-5], 'Cue1'] = cue1
            cue.at[column[10:-5], 'Cue2'] = cue2
            cue.at[column[10:-5], 'Cue3'] = cue3

    # Calculate the Knowledge metrics of the input
    cue1 = cue["Cue1"].sum()
    cue2 = cue1 / data["total_123"].sum()
    cue3 = 1 - cue2
    # Save the Knowledge metrics of the input
    cue.at["KNOWLEDGE", 'Cue1'] = cue1
    cue.at["KNOWLEDGE", 'Cue2'] = cue2
    cue.at["KNOWLEDGE", 'Cue3'] = cue3


    # Return the 3 DataFrames for RapidMiner usage
    return data, cue, DTF

test = pd.read_excel(os.path.normpath(os.path.expanduser("~/Documents/Internship/analysis-step/K-analysis-example-output.xlsx")))
#print(test)
DataF, C, DTF = rm_main(test)
#print(DataF)
#print(C)
DataF.to_excel(os.path.normpath(os.path.expanduser("~/Documents/Internship/analysis-step/SolAnalysis.xlsx")))
C.to_excel(os.path.normpath(os.path.expanduser("~/Documents/Internship/analysis-step/CueAnalysis.xlsx")))
#print(DTF)
DTF.to_excel(os.path.normpath(os.path.expanduser("~/Documents/Internship/analysis-step/venn.xlsx")))