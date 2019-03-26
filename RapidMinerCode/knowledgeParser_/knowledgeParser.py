# Import libraries
import rdflib
from rdflib import Graph, Namespace
from rdflib.util import guess_format
from rdflib.plugins.parsers.notation3 import N3Parser
from pathlib import Path
import pandas as pd
import os
import time
import re

# Class to handle the Excel file and relative indexes
class ExcelFile:
    def __init__(self, writer, num = -1):
        self.writer = writer
        self.index = 1
        self.num = num + 1

# Parse the given file and add its information to the file Excel given as third parameter
def parse(vocabFolder, date, row, list_):
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
        return list_, 0

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

    # Elaborate the fileName of the vocabulary
    fileName = date + "_" + row["prefix"] + "_" + row["VersionName"] + "_" + row["VersionDate"]
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(str(os.path.join(vocabFolder, fileName)) + ".xlsx", engine='xlsxwriter', options={'strings_to_urls': False, 'constant_memory': True, 'nan_inf_to_errors': True})
    excel = ExcelFile(writer)
    # Get the xlsxwriter workbook and worksheet objects.
    workbook  = writer.book
    # Add WorkSheets with relative titles and relative bold header 
    partialSheet = workbook.add_worksheet("Partial Triples")
    partialSheet.write_row(0, 0, ("Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"), workbook.add_format({"bold": True}))
    partialSheet.set_column(0, 8, 30)
    fullSheet = workbook.add_worksheet("Full Triples")
    fullSheet.write_row(0, 0, ("Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"), workbook.add_format({"bold": True}))
    fullSheet.set_column(0, 8, 30)
    
    # For each statement present in the graph obtained store the triples
    index = 0
    for subject, predicate, object_ in g:
        # Save the full statement to the ExcelSheet FullTriples
        fullSheet.write_row(excel.index, 0, (date, subject, predicate, object_, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
        subjectTerm = subject.replace("/", "#").split("#")
        subjectTerm = subjectTerm[len(subjectTerm)-1]
        predicateTerm = predicate.replace("/", "#").split("#")
        predicateTerm = predicateTerm[len(predicateTerm)-1]
        objectTerm = object_.replace("/", "#").split("#")
        objectTerm = objectTerm[len(objectTerm)-1]
        # Save the partial statement to the List to be added to the DataFrame
        list_.insert(index,{"Date": date, "Subject": subjectTerm, "Predicate": predicateTerm, "Object": objectTerm, "Domain": row["prefix"], "Domain Version": row["VersionName"], "Domain Date": row["VersionDate"], "URI": row["URI"], "Title": row["Title"], "Languages": row["Languages"]})
        index += 1
        # Save the partial statement to the ExcelSheet PartialTriples
        partialSheet.write_row(excel.index, 0, (date, subjectTerm, predicateTerm, objectTerm, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
        # Update the index of both the ExcelSheets
        excel.index += 1
        # If the rows reach the excel limit then create a new ExcelFile
        if(excel.index == 1048575):
            #Close the ExcelFile
            workbook.close()
            excel.writer.save()
            # Create a Pandas Excel writer using XlsxWriter as the engine.
            writer = pd.ExcelWriter(str(os.path.join(vocabFolder, fileName)) + str(excel.num) + ".xlsx", engine='xlsxwriter', options={'strings_to_urls': False, 'constant_memory': True, 'nan_inf_to_errors': True})
            excel = ExcelFile(writer, excel.num)
            # Get the xlsxwriter workbook and worksheet objects.
            workbook  = writer.book
            # Add WorkSheet with relative titles and relative bold header 
            partialSheet = workbook.add_worksheet("Partial Triples")
            partialSheet.write_row(0, 0, ("Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"), workbook.add_format({"bold": True}))
            partialSheet.set_column(0, 8, 30)
            # Add WorkSheet with relative titles and relative bold header 
            fullSheet = workbook.add_worksheet("Full Triples")
            fullSheet.write_row(0, 0, ("Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"), workbook.add_format({"bold": True}))
            fullSheet.set_column(0, 8, 30)

    # Close the Excel file of the single vocabulary
    excel.writer.book.close()
    excel.writer.save()

    # Return the List to be added to the DataFrame and the relative index
    return list_, index

# Mandatory function for RapidMiner
def rm_main(vocabs):
    # Create the folder used to store the results
    location = os.path.normpath(os.path.expanduser("~/Desktop/K-Files/"))
    if not os.path.isdir(location):
        os.makedirs(location)

    # Get the date of the current day of the Parsing
    date = time.strftime("%Y-%m-%d", time.gmtime())

    # Create the DataFrame to save the vocabs' Date of parsing, Subject, Predicate, Object, Domain, Domain Version, Domain Date, URI, Title, Languages
    df = pd.DataFrame(columns=["Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"])

    # Iterate for every vocabulary read from the second argument
    for index, row in vocabs.iterrows():
        # Create the Folder 
        vocabFolder = str(os.path.join(location, row["Folder"]))
        if not os.path.isdir(vocabFolder):
            os.makedirs(vocabFolder)
        
        # Add information for each vocabulary
        list_, i = parse(vocabFolder, date, row, list())
        # Save the information on the DataFrame for each vocabulary
        if(i and len(list_)):
            df = df.append(list_)

    # Return the DataFrame for RapidMiner visualization
    return df
    
print(rm_main(pd.read_excel(r"C:\Users\marco\Desktop\K-Files\latestKnowledge.xlsx")))

