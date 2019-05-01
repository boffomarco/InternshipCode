# Import libraries
import rdflib
from rdflib import Graph, RDFS
from rdflib.util import guess_format
from rdflib.plugins.parsers.notation3 import N3Parser
import pandas as pd
import os
import time
import networkx as nx

from datetime import datetime

# Logs the date with the string str to track errors 
def log(str_):
    ts = time.strftime("%Y-%m-%d %H:%M:%S - ", time.gmtime())
    f = open(os.path.normpath(os.path.expanduser("~/Desktop/K-Files/log.txt")), "a+")
    f.write(ts + str(str_) + "\n")
    f.close()

# Class to handle the Excel file and relative indexes
class ExcelFile:
    def __init__(self, writer, num = 0):
        self.writer = writer
        self.index = 1
        self.num = num + 1

# Parse the given file and add its information to the file Excel given as third parameter
def parse(vocabFolder, date, row, inTotalExcel, list_, predicates):

    print(row["prefix"])
    log(row["prefix"])

    tick_ = datetime.now()
    tick = datetime.now()

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
        return inTotalExcel, list_, 0

    tock = datetime.now()   
    diff = tock - tick    # the result is a datetime.timedelta object
    log("Parsing took " + str(diff.total_seconds()) + " seconds") 

    # Print number of rows before inheritance
    log(len(result))

    # Get the inTotalExcel file and relative worksheets
    inTotalWorkbook = inTotalExcel.writer.book
    inTotalSheet = inTotalWorkbook.get_worksheet_by_name("Inherited Total Triples")

    # Elaborate the fileName of the vocabulary
    inFileName = date + "_Inherited_" + row["prefix"] + "_" + row["VersionName"] + "_" + row["VersionDate"] + "_"
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    inSingleExcel, inSingleWorkbook, inSingleSheet = newExcel(0, str(os.path.join(vocabFolder, inFileName + "0.xlsx")), "Inherited Single Triples")

    tick = datetime.now()

    # Create the DataFrame used to save the table used to handle the inheritance relations
    inherit = pd.DataFrame(columns=["Subject", "subOf", "subbed"])
    # Create the set used to check if new Subject inheritance relation has to be added or if existing Subject inheritance relation has to be updated
    set_ = set()
    # Save inheritance relation between subject and object
    for s, o in g.subject_objects(RDFS.subClassOf):
        inherit, set_ = setInheritance(str(s), str(o), inherit, set_)
    # Create the networkx graph used to calculate inheritance
    nxG = createNXGraph(inherit)
    # Calculate the transitive_closure of the networkx graph to get all the possible inheritances
    nxGT = nx.transitive_closure(nxG)

    tock = datetime.now()   
    diff = tock - tick    # the result is a datetime.timedelta object
    log("Inheritance took " + str(diff.total_seconds()) + " seconds") 
    
    # Print number of rows of inheritance relations
    log(len(nxGT))

    tick = datetime.now()

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
            for pred in predicates["Predicate"]:
                if(pred == str(predicateTerm) or pred == str(predicate)):
                    bool_ = True
                    break
        # Check if the triple has to be saved
        if(bool_ == True):
            # Save the statement to the List to be added to the DataFrame
            list_.insert(index,{"Date": date, "Subject": subject, "Predicate": predicate, "Object": object_, "SubjectTerm": subjectTerm, "PredicateTerm": predicateTerm, "ObjectTerm": objectTerm, "Domain": row["prefix"], "Domain Version": row["VersionName"], "Domain Date": row["VersionDate"], "URI": row["URI"], "Title": row["Title"], "Languages": row["Languages"], "Inherited": 0})
            index += 1
            
            # Save the statement to the ExcelSheet Triples
            inSingleSheet.write_row(inSingleExcel.index, 0, (date, subject, predicate, object_, subjectTerm, predicateTerm, objectTerm, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"], 0))
            inTotalSheet.write_row(inTotalExcel.index, 0, (date, subject, predicate, object_, subjectTerm, predicateTerm, objectTerm, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"], 0))
            # Update the index of both the ExcelSheets
            inSingleExcel.index += 1
            inTotalExcel.index += 1

            # If the rows of inSingleExcel reach the excel limit then create a new ExcelFile
            if(inSingleExcel.index == 1048575):
                #Close the ExcelFile
                inSingleWorkbook.close()
                inSingleExcel.writer.save()
                # Create a new ExcelFile
                inSingleExcel, inSingleWorkbook, inSingleSheet = newExcel(inSingleExcel.num, str(os.path.join(vocabFolder, inFileName + str(inSingleExcel.num) + ".xlsx")), "Inherited Single Triples")
                
            # If the rows of totalExcel reach the excel limit then create a new ExcelFile
            if(inTotalExcel.index == 1048575):
                #Close the ExcelFile
                inTotalWorkbook.close()
                inTotalExcel.writer.save()
                # Create a new ExcelFile
                inTotalExcel, inTotalWorkbook, inTotalSheet = newExcel(inTotalExcel.num, str(os.path.join(os.path.dirname(vocabFolder), date + "_Inherited_Knowledge-Triples_" + str(inTotalExcel.num) + ".xlsx")), "Inherited Total Triples")

            for node in nxGT:
                for n in nxGT.neighbors(node):
                    if(str(n) == str(object_)):
                        # Compute the filtered statement of the Triples
                        nodeTerm = node.replace("/", "#").split("#")[-1]
                        if(not len(nodeTerm) and len(node.replace("/", "#").split("#")) > 1):
                            nodeTerm = node.replace("/", "#").split("#")[-2]
                        
                        # Save the statement to the List to be added to the DataFrame
                        list_.insert(index,{"Date": date, "Subject": subject, "Predicate": predicate, "Object": node, "SubjectTerm": subjectTerm, "PredicateTerm": predicateTerm, "ObjectTerm": nodeTerm, "Domain": row["prefix"], "Domain Version": row["VersionName"], "Domain Date": row["VersionDate"], "URI": row["URI"], "Title": row["Title"], "Languages": row["Languages"], "Inherited": 1})
                        index += 1
                        
                        # Save the statement to the ExcelSheet Triples
                        inSingleSheet.write_row(inSingleExcel.index, 0, (date, subject, predicate, node, subjectTerm, predicateTerm, nodeTerm, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"], 1))
                        inTotalSheet.write_row(inTotalExcel.index, 0, (date, subject, predicate, node, subjectTerm, predicateTerm, nodeTerm, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"], 1))
                        # Update the index of both the ExcelSheets
                        inSingleExcel.index += 1
                        inTotalExcel.index += 1

                        # If the rows of inSingleExcel reach the excel limit then create a new ExcelFile
                        if(inSingleExcel.index == 1048575):
                            #Close the ExcelFile
                            inSingleWorkbook.close()
                            inSingleExcel.writer.save()
                            # Create a new ExcelFile
                            inSingleExcel, inSingleWorkbook, inSingleSheet = newExcel(inSingleExcel.num, str(os.path.join(vocabFolder, inFileName + str(inSingleExcel.num) + ".xlsx")), "Inherited Single Triples")
                            
                        # If the rows of totalExcel reach the excel limit then create a new ExcelFile
                        if(inTotalExcel.index == 1048575):
                            #Close the ExcelFile
                            inTotalWorkbook.close()
                            inTotalExcel.writer.save()
                            # Create a new ExcelFile
                            inTotalExcel, inTotalWorkbook, inTotalSheet = newExcel(inTotalExcel.num, str(os.path.join(os.path.dirname(vocabFolder), date + "_Inherited_Knowledge-Triples_" + str(inTotalExcel.num) + ".xlsx")), "Inherited Total Triples")


    # Close the Excel file of the single vocabulary
    inSingleExcel.writer.book.close()
    inSingleExcel.writer.save()

    tock = datetime.now()   
    diff = tock - tick    # the result is a datetime.timedelta object
    log("Storing took " + str(diff.total_seconds()) + " seconds") 

    # Print number of rows after inheritance
    log(index)

    tock_ = datetime.now()   
    diff_ = tock_ - tick_    # the result is a datetime.timedelta object
    log("Inheriting took " + str(diff_.total_seconds()) + " seconds" + "\n") 
    print("Inheriting took " + str(diff_.total_seconds()) + " seconds") 

    # Return the List to be added to the DataFrame and the relative index
    return inTotalExcel, list_, index

# Create a new ExcelFile
def newExcel(excelNum, fileName, sheetName):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(fileName, engine='xlsxwriter', options={'strings_to_urls': False, 'constant_memory': True, 'nan_inf_to_errors': True})
    excelFile_ = ExcelFile(writer, excelNum)
    # Get the xlsxwriter workbook and worksheet objects.
    workbook  = writer.book
    # Add WorkSheet with relative titles and relative bold header 
    worksheet = workbook.add_worksheet(sheetName)
    worksheet.write_row(0, 0, ("Date", "Subject", "Predicate", "Object", "SubjectTerm", "PredicateTerm", "ObjectTerm", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages", "Inherited"), workbook.add_format({"bold": True}))
    worksheet.set_column(0, 12, 30)
    # Return the new excelFile_, workbook, worksheet
    return excelFile_, workbook, worksheet

# Set the inheritance
def setInheritance(subject, object_, inherit, set_):
    # Compute the length of the subject's set
    a = len(set_)
    # Add the subject to the set
    set_.add(subject)
    # Check if the length now is bigger, i.e. a new element has been added
    if(a < len(set_)):
        # Add the new subject and relative first inheritable object
        inherit.at[subject, "Subject"] = subject
        inherit.at[subject, "subOf"] = object_
        inherit.at[subject, "subbed"] = ""
    else:
        # Add a new inheritable object
        subOfs = str(inherit.at[subject, "subOf"])
        inherit.at[subject, "subOf"] = subOfs + " , " + object_
    # Return the dataframe and set relative to inheritance
    return inherit, set_

# Return the networkx graph used to calculate inheritance
def createNXGraph(inherit):
    # Create the networkx graph used to calculate inheritance
    nxG = nx.DiGraph()
    # Use this set to add a single node for every subject that inherit 
    nodes = set()

    # Iterate over every element of the dataframe containing the informations about inheritance
    for index, row in inherit.iterrows():
        # Get the relative inheritable objects of a subject
        subOfs = str(inherit.at[str(row["Subject"]), "subOf"])
        l = len(nodes)
        nodes.add(str(row["Subject"]))
        if(len(nodes) > l):
            nxG.add_node(str(row["Subject"]))
        for sub in subOfs.split(" , "):
            # Get the relative already inherited objects of a subject
            l = len(nodes)
            nodes.add(sub)
            if(len(nodes) > l):
                nxG.add_node(sub)
            nxG.add_edge(str(row["Subject"]), sub)

    # Return the networkx graph used to calculate inheritance
    return nxG

# Mandatory function for RapidMiner
def rm_main(vocabs, predicates = pd.DataFrame()):
    # Create the folder used to store the results
    location = os.path.normpath(os.path.expanduser("~/Desktop/K-Files/"))
    if not os.path.isdir(location):
        os.makedirs(location)

    # Get the date of the current day of the Parsing
    date = time.strftime("%Y-%m-%d", time.gmtime())

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    inTotalExcel, inTotalWorkbook, inTotalSheet = newExcel(0, str(os.path.join(location, date + "_Inherited_Knowledge-Triples_0.xlsx")), "Inherited Total Triples")

    # Create the DataFrame to save the vocabs' Date of parsing, Subject, Predicate, Object, Domain, Domain Version, Domain Date, URI, Title, Languages
    df = pd.DataFrame(columns=["Date", "Subject", "Predicate", "Object", "SubjectTerm", "PredicateTerm", "ObjectTerm", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages", "Inherited"])

    # Iterate for every vocabulary read from the second argument
    for index, row in vocabs.iterrows():
        # Create the Folder 
        vocabFolder = str(os.path.join(location, row["Folder"]))
        if not os.path.isdir(vocabFolder):
            os.makedirs(vocabFolder)
        print(row["Link"])
        # Add information for each vocabulary
        inTotalExcel, list_, i = parse(vocabFolder, date, row, inTotalExcel, list(), predicates)
        # Save the information on the DataFrame for each vocabulary
        if(i and len(list_)):
            df = df.append(list_)

    # Close the Excel file of the single vocabulary
    inTotalExcel.writer.book.close()
    inTotalExcel.writer.save()

    # Return the DataFrame for RapidMiner visualization
    return df

tick = datetime.now()

test = pd.read_excel(os.path.normpath(os.path.expanduser("~/Desktop/Internship/KnowDive/resources/KnowledgeLatest.xlsx")))
PrTest = pd.read_excel(os.path.normpath(os.path.expanduser("~/Desktop/Internship/InternshipCode/RapidMinerCode/knowledgeFilter/Predicate.xlsx")))
DTF = rm_main(test, PrTest)
DTF.to_excel(os.path.normpath(os.path.expanduser("~/Desktop/K-Files/Inherited_Triples.xlsx")))

tock = datetime.now()   
diff = tock - tick    # the result is a datetime.timedelta object
print(str(diff.total_seconds()) + " seconds") 