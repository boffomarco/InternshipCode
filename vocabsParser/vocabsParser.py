# Import libraries
from functions import os
from functions import Path
from functions import pd
from functions import ExcelFile
from functions import parse

# Extract the directory path to where to find the vocabs
originDir = os.path.dirname(os.path.abspath(__file__))
dir = os.path.join(os.path.dirname(os.path.dirname(originDir)) , "Resources")

# Iterate for every directory
for dirName in os.listdir(dir):
  # For each directory create a new ExcelFile
  if(os.path.isdir(os.path.join(dir, dirName))):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(os.path.join(originDir, dirName) + ".xlsx", engine='xlsxwriter', options={'strings_to_urls': False, 'constant_memory': True})
    excel = ExcelFile(writer)
    # Get the xlsxwriter workbook and worksheet objects.
    workbook  = writer.book
    # Add WorkSheet with relative title and relative bold header 
    data = workbook.add_worksheet("Data")
    data.write_row(0, 0, ("Subject", "Predicate", "Object", "Domain"), workbook.add_format({"bold": True}))
    data.set_column(0, 4, 66)

    # Add information for each file of the directory
    for fileName in os.listdir(os.path.join(dir, dirName)):
      excel = parse(dir, dirName, fileName, excel, originDir)

    # Close the Excel file
    excel.writer.book.close()
    excel.writer.save()