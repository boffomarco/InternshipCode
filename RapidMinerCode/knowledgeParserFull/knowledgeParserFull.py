# Import libraries
import rdflib
from rdflib import Graph, Namespace
from rdflib.util import guess_format
from rdflib.plugins.parsers.notation3 import N3Parser
import pandas as pd
import os
import time

# Class to handle the Excel file and relative indexes
class ExcelFile:
    def __init__(self, writer, num = 0):
        self.writer = writer
        self.index = 1
        self.num = num + 1

# Logs the date with the string str to track errors 
def log(location, str):
  ts = time.strftime("%Y-%m-%d %H:%M:%S - ", time.gmtime())
  f = open(os.path.join(location, "VSCode_log.txt"), "a+")
  f.write(ts + str + "\n")
  f.close()

# Mandatory function for RapidMiner
def rm_main(vocabs):
    # Create the folder used to store the results
    location = os.path.normpath(os.path.expanduser("~/Desktop/K-Files/"))
    if not os.path.isdir(location):
        os.makedirs(location)

    # Get the date of the current day of the Parsing
    date = time.strftime("%Y-%m-%d", time.gmtime())

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    totalWriter = pd.ExcelWriter(str(os.path.join(location, date + "_Full_Knowledge-Triples_0.xlsx")), engine='xlsxwriter', options={'strings_to_urls': False, 'constant_memory': True, 'nan_inf_to_errors': True})
    totalExcel = ExcelFile(totalWriter)
    # Get the xlsxwriter workbook and worksheet objects.
    totalWorkbook  = totalWriter.book
    totalFullSheet = totalWorkbook.add_worksheet("Total Full Triples")
    totalFullSheet.write_row(0, 0, ("Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"), totalWorkbook.add_format({"bold": True}))
    totalFullSheet.set_column(0, 8, 30)

    # Create the DataFrame to save the vocabs' Date of parsing, Subject, Predicate, Object, Domain, Domain Version, Domain Date, URI, Title, Languages
    df = pd.DataFrame(columns=["Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"])

    # Iterate for every vocabulary read from the second argument
    for index_, row in vocabs.iterrows():
        # Create the Folder 
        vocabFolder = str(os.path.join(location, row["Folder"]))
        if not os.path.isdir(vocabFolder):
            os.makedirs(vocabFolder)
        
        log(location, "Parsing     " + row["prefix"])

        # Create the list used to add the triples of the vocabulary to the DataFrame
        list_ = list()

        # Try to create the graph to analyze the vocabulary
        try:
            g = Graph()
            format_ = row["Link"].split(".")[-1]
            if(format_ == "txt"):
                format_ = row["Link"].split(".")[-2]
            format_ = format_.split("?")[0]
            result = g.parse(row["Link"], format=guess_format(format_), publicID=row["prefix"])
        except Exception as e:
            # In case of an error during the graph's initiation, print the error and return an empty list
            print(str(e) + "\n")

        log(location, "Serializing " + row["prefix"])

        # Serialize the vocabulary in a .nt format saved in vocabFolder/Resources with the same name of the Excel File
        try:
            resourceDestination = os.path.join(vocabFolder, "Resources")
            if not os.path.isdir(resourceDestination):
                os.makedirs(resourceDestination)
            fileName = date + "_" + row["prefix"] + "_" + row["VersionName"] + "_" + row["VersionDate"]
            g.serialize(destination=str(os.path.join(resourceDestination, fileName)) + ".nt", format='nt')
        except Exception as e:
            # In case of an error during the graph's serialization, print the error
            print(str(e) + "\n")

        # Get the totalExcel file and relative worksheets
        totalWorkbook = totalExcel.writer.book
        totalFullSheet = totalWorkbook.get_worksheet_by_name("Total Full Triples")

        # Elaborate the fileName of the vocabulary
        fileName = date + "_Full_" + row["prefix"] + "_" + row["VersionName"] + "_" + row["VersionDate"] + "_"
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        singleWriter = pd.ExcelWriter(str(os.path.join(vocabFolder, fileName + "0.xlsx")), engine='xlsxwriter', options={'strings_to_urls': False, 'constant_memory': True, 'nan_inf_to_errors': True})
        singleExcel = ExcelFile(singleWriter)
        # Get the xlsxwriter workbook and worksheet objects.
        singleWorkbook  = singleWriter.book
        singleFullSheet = singleWorkbook.add_worksheet("Single Full Triples")
        singleFullSheet.write_row(0, 0, ("Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"), singleWorkbook.add_format({"bold": True}))
        singleFullSheet.set_column(0, 8, 30)

        log(location, "Saving      " + row["prefix"] + " " + str(len(g)))
        
        # For each statement present in the graph obtained store the triples
        index = 0
        for subject, predicate, object_ in g:
            # Save the full statement to the ExcelSheet FullTriples
            singleFullSheet.write_row(singleExcel.index, 0, (date, subject, predicate, object_, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
            totalFullSheet.write_row(totalExcel.index, 0, (date, subject, predicate, object_, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
            # Save the Full statement to the List to be added to the DataFrame, and update the index
            list_.insert(index,{"Date": date, "Subject": subject, "Predicate": predicate, "Object": object_, "Domain": row["prefix"], "Domain Version": row["VersionName"], "Domain Date": row["VersionDate"], "URI": row["URI"], "Title": row["Title"], "Languages": row["Languages"]})
            index += 1
            # Update the index of both the ExcelSheets
            singleExcel.index += 1
            totalExcel.index += 1

            # If the rows reach the excel limit then create a new ExcelFile
            if(singleExcel.index == 1048575):
                #Close the ExcelFile
                singleWorkbook.close()
                singleExcel.writer.save()
                # Create a Pandas Excel writer using XlsxWriter as the engine.
                singleWriter = pd.ExcelWriter(str(os.path.join(vocabFolder, fileName + str(singleExcel.num) + ".xlsx")), engine='xlsxwriter', options={'strings_to_urls': False, 'constant_memory': True, 'nan_inf_to_errors': True})
                singleExcel = ExcelFile(singleWriter, singleExcel.num)
                # Get the xlsxwriter workbook and worksheet objects.
                singleWorkbook  = singleWriter.book
                # Add WorkSheet with relative titles and relative bold header 
                singleFullSheet = singleWorkbook.add_worksheet("Single Full Triples")
                singleFullSheet.write_row(0, 0, ("Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"), singleWorkbook.add_format({"bold": True}))
                singleFullSheet.set_column(0, 8, 30)

            # If the rows reach the excel limit then create a new ExcelFile
            if(totalExcel.index == 1048575):
                #Close the ExcelFile
                totalWorkbook.close()
                totalExcel.writer.save()

                # Create a Pandas Excel writer using XlsxWriter as the engine.
                totalWriter = pd.ExcelWriter(str(os.path.join(os.path.dirname(vocabFolder), date + "_Full_Knowledge-Triples_" + str(totalExcel.num) + ".xlsx")), engine='xlsxwriter', options={'strings_to_urls': False, 'constant_memory': True, 'nan_inf_to_errors': True})
                totalExcel = ExcelFile(totalWriter, totalExcel.num)
                # Get the xlsxwriter workbook and worksheet objects.
                totalWorkbook  = totalWriter.book
                # Add WorkSheet with relative titles and relative bold header 
                totalFullSheet = totalWorkbook.add_worksheet("Total Full Triples")
                totalFullSheet.write_row(0, 0, ("Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"), totalWorkbook.add_format({"bold": True}))
                totalFullSheet.set_column(0, 8, 30)

        # Close the Excel file of the single vocabulary
        singleExcel.writer.book.close()
        singleExcel.writer.save()
        
        # Save the information on the DataFrame for each vocabulary
        if(index and len(list_)):
            df = df.append(list_)

    # Close the Excel file of the total vocabularies
    totalExcel.writer.book.close()
    totalExcel.writer.save()

    # Return the DataFrame for RapidMiner storing module
    return df

rm_main(pd.read_excel(r"C:\Users\marco\Desktop\Internship\KnowDive\resources\KnowledgeFull.xlsx")).to_csv(r"C:\Users\marco\Desktop\K-Files\FullTriples.csv")