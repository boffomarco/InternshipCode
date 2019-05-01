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
def parse(vocabFolder, date, row, totalExcel, list_, predicates):
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

    # Serialize the vocabulary in multiple formats
    serializedName = date + "_" + row["prefix"] + "_" + row["VersionName"] + "_" + row["VersionDate"] + "."
    serializeVoc(vocabFolder, serializedName + "n3", g, "n3")
    serializeVoc(vocabFolder, serializedName + "nt", g, "nt")
    serializeVoc(vocabFolder, serializedName + "rdf", g, "pretty-xml")
    serializeVoc(vocabFolder, serializedName + "ttl", g, "turtle")
    serializeVoc(vocabFolder, serializedName + "json-ld", g, "json-ld")

    print(row["prefix"])

    # Get the totalExcel file and relative worksheets
    totalWorkbook = totalExcel.writer.book
    totalFilteredSheet = totalWorkbook.get_worksheet_by_name("Total Filtered Triples")

    # Elaborate the fileName of the vocabulary
    fileName = date + "_Filtered_" + row["prefix"] + "_" + row["VersionName"] + "_" + row["VersionDate"] + "_"
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    singleExcel, singleWorkbook, singleFilteredSheet = newExcel(0, str(os.path.join(vocabFolder, fileName + "0.xlsx")), "Single Filtered Triples")

    # For each statement present in the graph obtained store the triples
    index = 0
    for subject, predicate, object_ in g:
        # Compute the filtered statement of the Triples
        subjectTerm = subject.replace("/", "#").split("#")[-1]
        if(not len(subjectTerm) and len(subject.replace("/", "#").split("#")) > 1):
            subjectTerm = subject.replace("/", "#").split("#")[-2]
        predicateTerm = predicate.replace("/", "#").split("#")[-1]
        if(not len(predicateTerm) and len(predicate.replace("/", "#").split("#")) > 1):
            predicateTerm = predicate.replace("/", "#").split("#")[-2]
        objectTerm = object_.replace("/", "#").split("#")[-1]
        if(not len(objectTerm) and len(object_.replace("/", "#").split("#")) > 1):
            objectTerm = object_.replace("/", "#").split("#")[-2]
        if(row["prefix"] == "FreeBase"):
            subjectTerm = subjectTerm.split(".")[-1]
            if(not len(subjectTerm) and len(subjectTerm.split(".")) > 1):
                subjectTerm = subjectTerm.split(".")[-2]
            predicateTerm = predicateTerm.split(".")[-1]
            if(not len(objectTerm) and len(predicateTerm.split(".")) > 1):
                predicateTerm = predicateTerm.split(".")[-2]
            objectTerm = objectTerm.split(".")[-1]
            if(not len(objectTerm) and len(objectTerm.split(".")) > 1):
                objectTerm = objectTerm.split(".")[-2]

        # Check if the triple has to be saved, if there is a predicate selection then checks if that predicate has to be saved
        bool_ = False
        # If there is no predicate selection then save every triple
        if(len(predicates) == 0):
            bool_ = True
        # If there is a predicate selection then check if that predicate has to be saved
        else:
            for pred in predicates[data.columns[0]]:
                if(pred == str(predicateTerm) or pred == str(predicate)):
                    bool_ = True
                    break
        # Check if the triple has to be saved
        if(bool_ == True):
            # Save the Filtered statement to the List to be added to the DataFrame
            list_.insert(index,{"Date": date, "Subject": subjectTerm, "Predicate": predicateTerm, "Object": objectTerm, "Domain": row["prefix"], "Domain Version": row["VersionName"], "Domain Date": row["VersionDate"], "URI": row["URI"], "Title": row["Title"], "Languages": row["Languages"]})
            index += 1
            # Save the Filtered statement to the ExcelSheet FilteredTriples
            singleFilteredSheet.write_row(singleExcel.index, 0, (date, subjectTerm, predicateTerm, objectTerm, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
            totalFilteredSheet.write_row(totalExcel.index, 0, (date, subjectTerm, predicateTerm, objectTerm, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
            # Update the index of both the ExcelFiles
            singleExcel.index += 1
            totalExcel.index += 1
            # If the rows reach the excel limit then create a new ExcelFile
            if(singleExcel.index == 1048575):
                #Close the ExcelFile
                singleWorkbook.close()
                singleExcel.writer.save()
                # Create a new ExcelFile
                singleExcel, singleWorkbook, singleFilteredSheet = newExcel(singleExcel.num, str(os.path.join(vocabFolder, fileName + str(singleExcel.num) + ".xlsx")), "Single Filtered Triples")
            # If the rows reach the excel limit then create a new ExcelFile
            if(totalExcel.index == 1048575):
                #Close the ExcelFile
                totalExcel.writer.book.close()
                totalExcel.writer.save()
                # Create a new ExcelFile
                totalExcel, totalWorkbook, totalFilteredSheet = newExcel(totalExcel.num, str(os.path.join(os.path.dirname(vocabFolder), date + "_Filtered_Knowledge-Triples_" + str(totalExcel.num) + ".xlsx")), "Total Filtered Triples")

    # Close the Excel file of the single vocabulary
    singleExcel.writer.book.close()
    singleExcel.writer.save()

    # Return the List to be added to the DataFrame and the relative index
    return totalExcel, list_, index

# Serialize the vocabulary in a format saved in vocabFolder/Resources with the same name of the Excel File
def serializeVoc(vocabFolder, fileName, g, format_):
    try:
        resourceDestination = os.path.join(vocabFolder, "Resources/"+format_)
        if not os.path.isdir(resourceDestination):
            os.makedirs(resourceDestination)
        g.serialize(destination=str(os.path.join(resourceDestination, fileName)), format=format_)
    except Exception as e:
        # In case of an error during the graph's serialization, print the error
        print(str(e) + "\n")

# Create a new ExcelFile
def newExcel(excelNum, fileName, sheetName):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(fileName, engine='xlsxwriter', options={'strings_to_urls': False, 'constant_memory': True, 'nan_inf_to_errors': True})
    excelFile_ = ExcelFile(writer, excelNum)
    # Get the xlsxwriter workbook and worksheet objects.
    workbook  = writer.book
    # Add WorkSheet with relative titles and relative bold header 
    worksheet = workbook.add_worksheet(sheetName)
    worksheet.write_row(0, 0, ("Date", "SubjectTerm", "PredicateTerm", "ObjectTerm", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"), workbook.add_format({"bold": True}))
    worksheet.set_column(0, 8, 30)
    # Return the new excelFile_, workbook, worksheet
    return excelFile_, workbook, worksheet

# Mandatory function for RapidMiner
def rm_main(vocabs, predicates = pd.DataFrame()):
    # Create the folder used to store the results
    location = os.path.normpath(os.path.expanduser("~/Desktop/K-Files/"))
    if not os.path.isdir(location):
        os.makedirs(location)

    # Get the date of the current day of the Parsing
    date = time.strftime("%Y-%m-%d", time.gmtime())

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    totalExcel, totalWorkbook, totalFilteredSheet = newExcel(0, str(os.path.join(location, date + "_Filtered_Knowledge-Triples_0.xlsx")), "Total Filtered Triples")

    # Create the DataFrame to save the vocabs' Date of parsing, Subject, Predicate, Object, Domain, Domain Version, Domain Date, URI, Title, Languages
    df = pd.DataFrame(columns=["Date", "SubjectTerm", "PredicateTerm", "ObjectTerm", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"])

    # Iterate for every vocabulary read from the second argument
    for index, row in vocabs.iterrows():
        # Create the Folder 
        vocabFolder = str(os.path.join(location, row["Folder"]))
        if not os.path.isdir(vocabFolder):
            os.makedirs(vocabFolder)
        
        # Add information for each vocabulary
        totalExcel, list_, i = parse(vocabFolder, date, row, totalExcel, list(), predicates)
        # Save the information on the DataFrame for each vocabulary
        if(i and len(list_)):
            df = df.append(list_)

    # Close the Excel file of the single vocabulary
    totalExcel.writer.book.close()
    totalExcel.writer.save()

    # Return the DataFrame for RapidMiner visualization
    return df

test = pd.read_excel(os.path.normpath(os.path.expanduser("~/Desktop/Internship/KnowDive/resources/KnowledgeLatest.xlsx")))
PrTest = pd.read_excel(os.path.normpath(os.path.expanduser("~/Desktop/Internship/InternshipCode/RapidMinerCode/knowledgeFilter/Predicate.xlsx")))
DTF = rm_main(test, PrTest)
DTF.to_csv(os.path.normpath(os.path.expanduser("~/Desktop/K-Files/FilteredTriples.csv")))