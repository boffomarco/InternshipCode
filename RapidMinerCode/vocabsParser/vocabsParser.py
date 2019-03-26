
import pandas as pd

LOVVocabs = pd.read_excel(r"C:\Users\marco\Desktop\Internship\RapidMinerCode\LOV_Scraper\LOV.xlsx", sheet_name=1, header=None)
if(len(LOVVocabs)):
    # Iterate for every row of the LOV DataFrame
    #for index, row in LOVVocabs:
        # Save a list of statement for every file on the DataFrame given as input at the function
        print(LOVVocabs.iloc[0,0])