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

# Parse the given file and add its information to the file Excel given as third parameter
def parse(vocabFolder, date, row, totalExcel, list_):
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
        return totalExcel, list_, 0

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

    print(row["prefix"])

    # Get the totalExcel file and relative worksheets
    totalWorkbook = totalExcel.writer.book
    totalFilteredSheet = totalWorkbook.get_worksheet_by_name("Total Filtered Triples")
    """
    totalFullSheet = totalWorkbook.get_worksheet_by_name("Total Full Triples")
    """

    # Elaborate the fileName of the vocabulary
    fileName = date + "_Filtered_" + row["prefix"] + "_" + row["VersionName"] + "_" + row["VersionDate"] + "_"
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    singleWriter = pd.ExcelWriter(str(os.path.join(vocabFolder, fileName + "0.xlsx")), engine='xlsxwriter', options={'strings_to_urls': False, 'constant_memory': True, 'nan_inf_to_errors': True})
    singleExcel = ExcelFile(singleWriter)
    # Get the xlsxwriter workbook and worksheet objects.
    singleWorkbook  = singleWriter.book
    # Add WorkSheets with relative titles and relative bold header 
    singleFilteredSheet = singleWorkbook.add_worksheet("Single Filtered Triples")
    singleFilteredSheet.write_row(0, 0, ("Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"), singleWorkbook.add_format({"bold": True}))
    singleFilteredSheet.set_column(0, 8, 30)
    """
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
    """
    
    # For each statement present in the graph obtained store the triples
    index = 0
    for subject, predicate, object_ in g:
        # Save the full statement to the ExcelSheet FullTriples
        """
        singleFullSheet.write_row(singleExcel.index, 0, (date, subject, predicate, object_, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
        totalFullSheet.write_row(totalExcel.index, 0, (date, subject, predicate, object_, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
        """
        subjectTerm = subject.replace("/", "#").split("#")[-1]
        predicateTerm = predicate.replace("/", "#").split("#")[-1]
        objectTerm = object_.replace("/", "#").split("#")[-1]
        if(row["prefix"] == "FreeBase"):
            subjectTerm = subjectTerm.split(".")[-1]
            predicateTerm = predicateTerm.split(".")[-1]
            objectTerm = objectTerm.split(".")[-1]
        # Save the Filtered statement to the List to be added to the DataFrame
        list_.insert(index,{"Date": date, "Subject": subjectTerm, "Predicate": predicateTerm, "Object": objectTerm, "Domain": row["prefix"], "Domain Version": row["VersionName"], "Domain Date": row["VersionDate"], "URI": row["URI"], "Title": row["Title"], "Languages": row["Languages"]})
        """
        list_.insert(index,{"Date": date, "Subject": subject, "Predicate": predicate, "Object": object_, "Domain": row["prefix"], "Domain Version": row["VersionName"], "Domain Date": row["VersionDate"], "URI": row["URI"], "Title": row["Title"], "Languages": row["Languages"]})
        """
        index += 1
        # Save the Filtered statement to the ExcelSheet FilteredTriples
        singleFilteredSheet.write_row(singleExcel.index, 0, (date, subjectTerm, predicateTerm, objectTerm, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
        totalFilteredSheet.write_row(totalExcel.index, 0, (date, subjectTerm, predicateTerm, objectTerm, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
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
            singleFilteredSheet = singleWorkbook.add_worksheet("Single Filtered Triples")
            singleFilteredSheet.write_row(0, 0, ("Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"), singleWorkbook.add_format({"bold": True}))
            singleFilteredSheet.set_column(0, 8, 30)
            """
            # Add WorkSheet with relative titles and relative bold header 
            singleFullSheet = singleWorkbook.add_worksheet("Single Full Triples")
            singleFullSheet.write_row(0, 0, ("Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"), singleWorkbook.add_format({"bold": True}))
            singleFullSheet.set_column(0, 8, 30)
            """
        # If the rows reach the excel limit then create a new ExcelFile
        if(totalExcel.index == 1048575):
            #Close the ExcelFile
            totalWorkbook.close()
            totalExcel.writer.save()
            # Create a Pandas Excel writer using XlsxWriter as the engine.
            totalWriter = pd.ExcelWriter(str(os.path.join(os.path.dirname(vocabFolder), date + "_Filtered_Knowledge-Triples_" + str(totalExcel.num) + ".xlsx")), engine='xlsxwriter', options={'strings_to_urls': False, 'constant_memory': True, 'nan_inf_to_errors': True})
            totalExcel = ExcelFile(totalWriter, totalExcel.num)
            # Get the xlsxwriter workbook and worksheet objects.
            totalWorkbook  = totalWriter.book
            # Add WorkSheet with relative titles and relative bold header 
            totalFilteredSheet = totalWorkbook.add_worksheet("Total Filtered Triples")
            totalFilteredSheet.write_row(0, 0, ("Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"), totalWorkbook.add_format({"bold": True}))
            totalFilteredSheet.set_column(0, 8, 30)
            """
            # Create a Pandas Excel writer using XlsxWriter as the engine.
            totalWriter = pd.ExcelWriter(str(os.path.join(os.path.dirname(vocabFolder), date + "_Full_Knowledge-Triples_" + str(totalExcel.num) + ".xlsx")), engine='xlsxwriter', options={'strings_to_urls': False, 'constant_memory': True, 'nan_inf_to_errors': True})
            totalExcel = ExcelFile(totalWriter, totalExcel.num)
            # Get the xlsxwriter workbook and worksheet objects.
            totalWorkbook  = totalWriter.book
            # Add WorkSheet with relative titles and relative bold header 
            totalFullSheet = totalWorkbook.add_worksheet("Total Full Triples")
            totalFullSheet.write_row(0, 0, ("Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"), totalWorkbook.add_format({"bold": True}))
            totalFullSheet.set_column(0, 8, 30)
            """

    # Close the Excel file of the single vocabulary
    singleExcel.writer.book.close()
    singleExcel.writer.save()

    # Return the List to be added to the DataFrame and the relative index
    return totalExcel, list_, index

# Mandatory function for RapidMiner
def rm_main(vocabs):
    # Create the folder used to store the results
    location = os.path.normpath(os.path.expanduser("~/Desktop/K-Files/"))
    if not os.path.isdir(location):
        os.makedirs(location)

    # Get the date of the current day of the Parsing
    date = time.strftime("%Y-%m-%d", time.gmtime())

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    totalWriter = pd.ExcelWriter(str(os.path.join(location, date + "_Filtered_Knowledge-Triples_0.xlsx")), engine='xlsxwriter', options={'strings_to_urls': False, 'constant_memory': True, 'nan_inf_to_errors': True})
    totalExcel = ExcelFile(totalWriter)
    # Get the xlsxwriter workbook and worksheet objects.
    totalWorkbook  = totalWriter.book
    # Add WorkSheets with relative titles and relative bold header 
    totalFilteredSheet = totalWorkbook.add_worksheet("Total Filtered Triples")
    totalFilteredSheet.write_row(0, 0, ("Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"), totalWorkbook.add_format({"bold": True}))
    totalFilteredSheet.set_column(0, 8, 30)
    """
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    totalWriter = pd.ExcelWriter(str(os.path.join(location, date + "_Full_Knowledge-Triples_0.xlsx")), engine='xlsxwriter', options={'strings_to_urls': False, 'constant_memory': True, 'nan_inf_to_errors': True})
    totalExcel = ExcelFile(totalWriter)
    # Get the xlsxwriter workbook and worksheet objects.
    totalWorkbook  = totalWriter.book
    totalFullSheet = totalWorkbook.add_worksheet("Total Full Triples")
    totalFullSheet.write_row(0, 0, ("Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"), totalWorkbook.add_format({"bold": True}))
    totalFullSheet.set_column(0, 8, 30)
    """

    # Create the DataFrame to save the vocabs' Date of parsing, Subject, Predicate, Object, Domain, Domain Version, Domain Date, URI, Title, Languages
    df = pd.DataFrame(columns=["Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"])

    # Iterate for every vocabulary read from the second argument
    for index, row in vocabs.iterrows():
        # Create the Folder 
        vocabFolder = str(os.path.join(location, row["Folder"]))
        if not os.path.isdir(vocabFolder):
            os.makedirs(vocabFolder)
        
        # Add information for each vocabulary
        totalExcel, list_, i = parse(vocabFolder, date, row, totalExcel, list())
        # Save the information on the DataFrame for each vocabulary
        if(i and len(list_)):
            df = df.append(list_)

    # Close the Excel file of the single vocabulary
    totalExcel.writer.book.close()
    totalExcel.writer.save()

    # Return the DataFrame for RapidMiner visualization
    return df
    
print(rm_main(pd.read_excel(r"C:\Users\marco\Desktop\K-Files\KnowledgeLatest.xlsx")))

