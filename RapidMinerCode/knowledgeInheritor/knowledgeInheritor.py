# Import libraries
import rdflib
from rdflib import Graph
from rdflib.util import guess_format
from rdflib.plugins.parsers.notation3 import N3Parser
import pandas as pd
import os
import time

from datetime import datetime

# Class to handle the Excel file and relative indexes
class ExcelFile:
    def __init__(self, writer, num = 0):
        self.writer = writer
        self.index = 1
        self.num = num + 1

# Parse the given file and add its information to the file Excel given as third parameter
def parse(vocabFolder, date, row, inTotalExcel, list_):
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

    print(row["prefix"])

    # Get the inTotalExcel file and relative worksheets
    inTotalWorkbook = inTotalExcel.writer.book
    inTotalFilteredSheet = inTotalWorkbook.get_worksheet_by_name("Inherited Total Filtered T.")

    # Elaborate the fileName of the vocabulary
    inFileName = date + "_Inherited_Filtered_" + row["prefix"] + "_" + row["VersionName"] + "_" + row["VersionDate"] + "_"
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    inSingleExcel, inSingleWorkbook, inSingleFilteredSheet = newExcel(0, str(os.path.join(vocabFolder, inFileName + "0.xlsx")), "Single Inherited Filtered T.")

    # Create the DataFrame used to save the table used to handle the inheritance relations
    inherit = pd.DataFrame(columns=["Subject", "subOf", "subbed"])
    # Create the set used to check if new Subject inheritance relation has to be added or if existing Subject inheritance relation has to be updated
    set_ = set()
    # For each statement present in the graph obtained store the triples
    index = 0
    for subject, predicate, object_ in g:

        # Save inheritance relation between subject and object
        if("subClassOf" in predicate or "subPropertyOf" in predicate):
            inherit, set_ = setInheritance(str(subject), str(object_), inherit, set_)

        """
        # Save the full statement to the ExcelSheet FullTriples
        inSingleFullSheet.write_row(inSingleExcel.index, 0, (date, subject, predicate, object_, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
        inTotalFullSheet.write_row(totalExcel.index, 0, (date, subject, predicate, object_, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
        """
        
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
        
        # Save the Filtered statement to the List to be added to the DataFrame
        #list_.insert(index,{"Date": date, "Subject": subject, "Predicate": predicate, "Object": object_, "Domain": row["prefix"], "Domain Version": row["VersionName"], "Domain Date": row["VersionDate"], "URI": row["URI"], "Title": row["Title"], "Languages": row["Languages"]})
        list_.insert(index,{"Date": date, "Subject": subjectTerm, "Predicate": predicateTerm, "Object": objectTerm, "Domain": row["prefix"], "Domain Version": row["VersionName"], "Domain Date": row["VersionDate"], "URI": row["URI"], "Title": row["Title"], "Languages": row["Languages"]})
        index += 1
        
        # Save the Filtered statement to the ExcelSheet FilteredTriples
        inSingleFilteredSheet.write_row(inSingleExcel.index, 0, (date, subjectTerm, predicateTerm, objectTerm, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
        inTotalFilteredSheet.write_row(inTotalExcel.index, 0, (date, subjectTerm, predicateTerm, objectTerm, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
        # Update the index of both the ExcelSheets
        inSingleExcel.index += 1
        inTotalExcel.index += 1

        # If the rows of inSingleExcel reach the excel limit then create a new ExcelFile
        if(inSingleExcel.index == 1048575):
            #Close the ExcelFile
            inSingleWorkbook.close()
            inSingleExcel.writer.save()
            # Create a new ExcelFile
            inSingleExcel, inSingleWorkbook, inSingleFilteredSheet = newExcel(inSingleExcel.num, str(os.path.join(vocabFolder, inFileName + str(inSingleExcel.num) + ".xlsx")), "Single Filtered Triples")
            
        # If the rows of totalExcel reach the excel limit then create a new ExcelFile
        if(inTotalExcel.index == 1048575):
            #Close the ExcelFile
            inTotalExcel.book.close()
            inTotalExcel.writer.save()
            # Create a new ExcelFile
            inTotalExcel, inTotalWorkbook, inTotalFilteredSheet = newExcel(inTotalExcel.num, str(os.path.join(os.path.dirname(vocabFolder), date + "_Filtered_Knowledge-Triples_" + str(inTotalExcel.num) + ".xlsx")), "Total Filtered Triples")

    # Print number of rows before inheritance
    print(index)

    # Add the inheritance relative triples
    if(len(inherit)):
        # Generate the list with all the relative inherited triples
        check, inList, inIndex, inherit = addInheritance(g, inherit)
        # Iteratively repeat the controls to add all the inherited triples
        while(check):
            # Iterate on every element/triple of the list and add the value to the excel files
            for element in inList:
                # Extract the triple from the element
                subject = element["Subject"]
                predicate = element["Predicate"]
                object_ = element["Object"]

                """
                # Save the full statement to the ExcelSheet FullTriples
                inSingleFullSheet.write_row(inSingleExcel.index, 0, (date, subject, predicate, object_, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
                inTotalFullSheet.write_row(totalExcel.index, 0, (date, subject, predicate, object_, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
                """
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
                
                # Save the Filtered statement to the List to be added to the DataFrame
                #list_.insert(index,{"Date": date, "Subject": subject, "Predicate": predicate, "Object": object_, "Domain": row["prefix"], "Domain Version": row["VersionName"], "Domain Date": row["VersionDate"], "URI": row["URI"], "Title": row["Title"], "Languages": row["Languages"]})
                list_.insert(index,{"Date": date, "Subject": subjectTerm, "Predicate": predicateTerm, "Object": objectTerm, "Domain": row["prefix"], "Domain Version": row["VersionName"], "Domain Date": row["VersionDate"], "URI": row["URI"], "Title": row["Title"], "Languages": row["Languages"]})
                index += 1
                
                # Save the Filtered statement to the ExcelSheet FilteredTriples
                inSingleFilteredSheet.write_row(inSingleExcel.index, 0, (date, subjectTerm, predicateTerm, objectTerm, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
                inTotalFilteredSheet.write_row(inTotalExcel.index, 0, (date, subjectTerm, predicateTerm, objectTerm, row["prefix"], row["VersionName"], row["VersionDate"], row["URI"], row["Title"], row["Languages"]))
                # Update the index of both the ExcelSheets
                inSingleExcel.index += 1
                inTotalExcel.index += 1

                # If the rows of inSingleExcel reach the excel limit then create a new ExcelFile
                if(inSingleExcel.index == 1048575):
                    #Close the ExcelFile
                    inSingleWorkbook.close()
                    inSingleExcel.writer.save()
                    # Create a new ExcelFile
                    inSingleExcel, inSingleWorkbook, inSingleFilteredSheet = newExcel(inSingleExcel.num, str(os.path.join(vocabFolder, inFileName + str(inSingleExcel.num) + ".xlsx")), "Single Filtered Triples")
                    
                # If the rows of totalExcel reach the excel limit then create a new ExcelFile
                if(inTotalExcel.index == 1048575):
                    #Close the ExcelFile
                    inTotalExcel.book.close()
                    inTotalExcel.writer.save()
                    # Create a new ExcelFile
                    inTotalExcel, inTotalWorkbook, inTotalFilteredSheet = newExcel(inTotalExcel.num, str(os.path.join(os.path.dirname(vocabFolder), date + "_Filtered_Knowledge-Triples_" + str(inTotalExcel.num) + ".xlsx")), "Total Filtered Triples")

            # Generate the list with all the relative inherited triples
            check, inList, inIndex, inherit = addInheritance(g, inherit)

    # Print number of rows after inheritance
    print(index)

    # Close the Excel file of the single vocabulary
    inSingleExcel.writer.book.close()
    inSingleExcel.writer.save()

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
    worksheet.write_row(0, 0, ("Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"), workbook.add_format({"bold": True}))
    worksheet.set_column(0, 8, 30)
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

# Add the inherited triples to a list
def addInheritance(g, inherit):
    # Get the set of subjects/terms that need inheritance
    termL = set()
    # Get the set of objects that need to be inherited
    subL = set()
    # Iterate over every element of the dataframe containing the informations about inheritance
    for index, row in inherit.iterrows():
        subEq = False
        # Get the relative inheritable objects of a subject
        subOfs = str(inherit.at[str(row["Subject"]), "subOf"])
        for sub in subOfs.split(" , "):
            # Get the relative already inherited objects of a subject
            subs = str(inherit.at[str(row["Subject"]), "subbed"])
            # Add an inheritable object only if it has not already been inherited
            if(sub not in subs.split(" , ")):
                subL.add(sub)
                subEq = True
        # Add a subject/term only if it has to get other inheritances
        if(subEq):
            term = str(row["Subject"])
            termL.add(term)

    # Return False if there is nothing to be added
    if(not len(subL)):
        return False, list(), 0, inherit

    # Create a new set to contain only those objects that has already inherited every inheritable objects
    toSubList = subL.copy()
    # Remove from the set of subOfs to get the terms on top that has to be inherited
    # Iterate over every combination on subjects/terms and objects/subs
    for term in termL:
        for sub in subL:
            # If an subject/term still needs inheritance, remove it from the set of inheritable objects
            if(term == sub):
                toSubList.remove(term)

    # Create the list and index used to contain all the inherited triples
    inList_ = list()
    inIndex = 0
    # Continue only in case of inheritance
    if(len(toSubList)):
        # Create the set of subjects/termList that needs immediate inheritance
        termList = set()
        # Iterate over every subject/term that need inheritance
        for term in termL:
            # Create a set for every subject/term, containing its relative inheritable objects/sub
            subL = set()
            # Get and iterate over the already inheritable objects/subOfs of the subject/term
            subOfs = str(inherit.at[term, "subOf"])
            for sub in subOfs.split(" , "):
                # Add the inheritable objects to the set of the subject/term
                subL.add(sub)
            # Iterate over every object/toSub that is going to be inherited
            for toSub in toSubList:
                # If this object/toSub is a subject, then inherit also its relative objects/subOfs
                if(toSub in inherit["Subject"]):
                    # Get and iterate over the inherited objects/toSubOfs of the object/toSub that need inheritance from the subject/term
                    toSubOfs = str(inherit.at[toSub, "subOf"])
                    for sub in toSubOfs.split(" , "):
                        # Compute the length of the subject/term's set
                        a = len(subL)
                        # Add the inheritable object/sub to the set of the subject/term
                        subL.add(sub)
                        # Check if the length now is bigger, i.e. a new object/sub has been added
                        if(a < len(subL)):
                            # Add the new object/sub to the inheritable objects/subOfs on the subject/term set and relative row of the dataframe
                            subOfs = str(inherit.at[term, "subOf"])
                            inherit.at[term, "subOf"] = subOfs + " , " + sub
            # Add only the terms that can inherit object/toSub
            if(toSub in str(inherit.at[term, "subOf"])):
                termList.add(term)

        # Iterate over every subject/term that needs inheritance
        for term in termList:
            # Get the inheritable objects/subOfs of the subject/term
            subOfs = str(inherit.at[term, "subOf"])
            # Iterate over every object/toSub that is going to be inherited
            for toSub in toSubList:
                # If the combination match, i.e. a subject/term needs to inherit from the object/toSub
                if(toSub in subOfs):
                    # Get the already inherited/subbed objects/subs of the subject/term
                    subs = str(inherit.at[term, "subbed"])
                    # Add the object/toSub to the already inherited/subbed objects/subs of the subject/term
                    inherit.at[term, "subbed"] = subs + " , " + str(toSub)

                    # Add the triples having the object/toSub as Subject as if the subject/term is the actual Subject 
                    # Iterate over every triple of the graph
                    for subject, predicate, object_ in g:
                        # If the object/toSub acts as Subject of that triple
                        if(toSub in subject):
                            # Add the triple as if the subject/term is the actual Subject 
                            inList_.insert(inIndex, {"Subject": str(term), "Predicate": str(predicate), "Object": str(object_)})
                            inIndex += 1

        # Return True, the list with the inherited triples and the relative index number
        return True, inList_, inIndex, inherit
    # If there is nothing to be added
    else: 
        # Return False
        return False, inList_, 0, inherit

# Mandatory function for RapidMiner
def rm_main(vocabs):
    # Create the folder used to store the results
    location = os.path.normpath(os.path.expanduser("~/Desktop/K-Files/"))
    if not os.path.isdir(location):
        os.makedirs(location)

    # Get the date of the current day of the Parsing
    date = time.strftime("%Y-%m-%d", time.gmtime())

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    inTotalExcel, inTotalWorkbook, inTotalFilteredSheet = newExcel(0, str(os.path.join(location, date + "_Inherited_Filtered_Knowledge-Triples_0.xlsx")), "Inherited Total Filtered T.")

    # Create the DataFrame to save the vocabs' Date of parsing, Subject, Predicate, Object, Domain, Domain Version, Domain Date, URI, Title, Languages
    df = pd.DataFrame(columns=["Date", "Subject", "Predicate", "Object", "Domain", "Domain Version", "Domain Date", "URI", "Title", "Languages"])

    # Iterate for every vocabulary read from the second argument
    for index, row in vocabs.iterrows():
        # Create the Folder 
        vocabFolder = str(os.path.join(location, row["Folder"]))
        if not os.path.isdir(vocabFolder):
            os.makedirs(vocabFolder)
        
        # Add information for each vocabulary
        inTotalExcel, list_, i = parse(vocabFolder, date, row, inTotalExcel, list())
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
DTF = rm_main(test)
DTF.to_excel(os.path.normpath(os.path.expanduser("~/Desktop/K-Files/Inherited_Triples.xlsx")))

tock = datetime.now()   
diff = tock - tick    # the result is a datetime.timedelta object
print(str(diff.total_seconds()) + " seconds") 