# Import libraries
from functions import vocabList
from functions import ExcelFile
from functions import pd
from functions import Path
import os

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter("./LOV.xlsx", engine='xlsxwriter')
excel = ExcelFile(writer)
# Get the xlsxwriter workbook and worksheet objects.
workbook  = writer.book
# Add WorkSheets with relative titles and relative bold header 
meta = workbook.add_worksheet("Metadata")
meta.write_row(0, 0, ("prefix", "Title", "URI", "Namespace", "homepage", "Description", "Classes", "Properties", "Datatypes", "Instances"), workbook.add_format({"bold": True}))
meta.set_column(0, 9, 30)
languages = workbook.add_worksheet("Languages")
languages.write_row(0, 0, ("prefix", "name", "uri"), workbook.add_format({"bold": True}))
languages.set_column(0, 2, 30)
creators = workbook.add_worksheet("Creators")
creators.write_row(0, 0, ("prefix", "name", "uri"), workbook.add_format({"bold": True}))
creators.set_column(0, 2, 30)
contributors = workbook.add_worksheet("Contributors")
contributors.write_row(0, 0, ("prefix", "name", "uri"), workbook.add_format({"bold": True}))
contributors.set_column(0, 2, 30)
publishers = workbook.add_worksheet("Publishers")
publishers.write_row(0, 0, ("prefix", "name", "uri"), workbook.add_format({"bold": True}))
publishers.set_column(0, 2, 30)
expressivity = workbook.add_worksheet("Expressivity")
expressivity.write_row(0, 0, ("prefix", "expressivity"), workbook.add_format({"bold": True}))
expressivity.set_column(0, 1, 30)
tags = workbook.add_worksheet("Tags")
tags.write_row(0, 0, ("prefix", "tag"), workbook.add_format({"bold": True}))
tags.set_column(0, 1, 30)
links = workbook.add_worksheet("Links")
links.write_row(0, 0, ("prefix", "direction", "type", "link"), workbook.add_format({"bold": True}))
links.set_column(0, 3, 30)

# Extract the directory path to store the data
dir = Path(__file__).parents[2]

# Create the directory if not present
if not os.path.isdir(os.path.join(str(dir), "Resources/LOV")):
    os.makedirs(os.path.join(str(dir), "Resources/LOV"))

# Set the URL you want to webscrape from
url = "https://lov.linkeddata.es"
# Set the starting and ending page to scrape, that updates dynamically
page = 1
end = 2

# Scrape every page from the vocabs tab of LOV
while page < end:
    # Get the #page with the vocabs list
    link = url+"/dataset/lov/vocabs?&page="+str(page)
    end = vocabList(link, url, end, excel)
    # Iterate the next page if there were vocabs in this page, otherwise end the program here
    page += 1

# Close the Excel file
workbook.close()
writer.save()
