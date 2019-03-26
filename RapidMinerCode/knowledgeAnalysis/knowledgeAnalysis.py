# Import libraries
import pandas as pd

# Mandatory function for RapidMiner
def rm_main(data):
    # Drop the column 'in documents', that is equal to 'total'
    data.drop("in documents", axis=1, inplace=True)

    # Create the DataFrame used to save the occurrences of the Names present on the Element row
    DF = pd.DataFrame(columns=["Element", "Names"])
    # Iterate for every row present on data, for every Element
    for index, row in data.iterrows():
        # Create a list to save the Names present on that row
        list_ = list()
        # For evert column that indicates a Name
        for column in data:
            # Check if the Name is present on that Element/row
            if("in class" in column and row[column]): 
                # Save the Name on the list
                name = column[10:-1]
                list_.append(name)
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

    # Create the DataFrame used to save the Cues
    cue = pd.DataFrame(columns=["Class","Cue1", "Cue2", "Cue3"])
    # Iterate for every column present on data
    for column in data:
        # Checks if the column identify a Class
        if("in class" in column):
            # Create the new column for the Cue in the input DataFrame, and calculate the values for every Element 
            index = data.columns.get_loc(column)
            className = "Cue(" + column[10:-1] + ")"
            tempColumn = data[column] / data["total"]
            data.insert(index, className, tempColumn)
            
            # Calculate the metrics of that Class
            cue1 = data[className].sum()
            cue2 = cue1 / data[column].sum()
            cue3 = 1 - cue2
            # Save the metrics of that Class
            cue.at[column[10:-1], 'Class'] = column[10:-1]
            cue.at[column[10:-1], 'Cue1'] = cue1
            cue.at[column[10:-1], 'Cue2'] = cue2
            cue.at[column[10:-1], 'Cue3'] = cue3

    # Calculate the Knowledge metrics of the input
    cue1 = cue["Cue1"].sum()
    cue2 = cue1 / data["total"].sum()
    cue3 = 1 - cue2
    # Save the Knowledge metrics of the input
    cue.at["KNOWLEDGE", 'Class'] = "KNOWLEDGE"
    cue.at["KNOWLEDGE", 'Cue1'] = cue1
    cue.at["KNOWLEDGE", 'Cue2'] = cue2
    cue.at["KNOWLEDGE", 'Cue3'] = cue3

    # Return the 3 DataFrames for RapidMiner usage
    return data, cue, DTF


DataF, C, DTF = rm_main(pd.read_excel(r"C:\Users\marco\Desktop\analysis-step\K-analysis-example-output.xlsx"))
#print(DataF)
#print(C)
#DataF.to_excel(r"C:\Users\marco\Desktop\analysis-step\SolAnalysis.xlsx")
#C.to_excel(r"C:\Users\marco\Desktop\analysis-step\CueAnalysis.xlsx")
#print(DTF)
DTF.to_excel(r"C:\Users\marco\Desktop\analysis-step\venn.xlsx")