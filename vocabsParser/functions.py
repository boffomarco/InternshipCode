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

# Parse the given file and add its information to the file Excel given as third parameter
def parse(dir, dirName, file, excel, originDir):
  root = os.path.join(dir, dirName) 
  # Create a graph to analyze the n3 file
  try:
    g = Graph()
    log("Parsing : " + file + "\n")
    fileObj = open(os.path.join(root, file), "r",encoding="utf8")
    result = g.parse(file = fileObj, format=guess_format(file), publicID=file)
    fileObj.close()
    log("Parsed : " + file + "\n")
  except Exception as e:
    if "Bad syntax (Prefix" in str(e):
      try:
        g = Graph()
        log("Trying to reParsing " + file + "\n")
        line_prepender(os.path.join(root, file))
        fileObj = open(os.path.join(root, file), "r",encoding="utf8")
        result = g.parse(file = fileObj, format=guess_format(file), publicID=file)
        fileObj.close()
        log("Parsed " + file + "\n")
      except Exception as e:
        log("Error trying to parse " + file + "\n")
        log(str(e) + "\n")
        return excel
    else:
      log("Error trying to parse " + file + "\n")
      log(str(e) + "\n")
      return excel

  # Get the excel file and relative worksheet
  workbook = excel.writer.book
  data = workbook.get_worksheet_by_name("Data")
  
  # For each statement present in the graph obtained
  for subject, predicate, object_ in g:
    # Save the statement to the ExcelFile
    predicateTerm = predicate.replace("/", "#").split("#")
    predicateTerm = predicateTerm[len(predicateTerm)-1]
    objectTerm = object_.replace("/", "#").split("#")
    objectTerm = objectTerm[len(objectTerm)-1]
    domain = file.replace("_", ".").split(".")[0]
    data.write_row(excel.index, 0, (subject, predicateTerm, objectTerm, domain))
    excel.index += 1
    # If the rows reach the excel limit then create a new ExcelFile
    if(excel.index == 1048575):
      #Close the ExcelFile
      workbook.close()
      excel.writer.save()
      # Create a Pandas Excel writer using XlsxWriter as the engine.
      writer = pd.ExcelWriter(os.path.join(originDir, dirName) + str(excel.num) + ".xlsx", engine='xlsxwriter', options={'strings_to_urls': False, 'constant_memory': True})
      excel = ExcelFile(writer, excel.num)
      # Get the xlsxwriter workbook and worksheet objects.
      workbook  = writer.book
      # Add WorkSheet with relative title and relative bold header 
      data = workbook.add_worksheet("Data")
      data.write_row(0, 0, ("Subject", "Predicate", "Object", "Domain"), workbook.add_format({"bold": True}))
      data.set_column(0, 4, 66)

  return excel

# Logs the date with the string str to track errors 
def log(str):
  ts = time.strftime("%Y-%m-%d %H:%M:%S - ", time.gmtime())
  f = open("log.txt", "a+")
  f.write(ts + str)
  f.close()


# Class to handle the Excel file and relative indexes
class ExcelFile:
  def __init__(self, writer, num = -1):
    self.writer = writer
    self.index = 1
    self.num = num + 1

def line_prepender(filename):
    with open(filename, 'r+') as f:
        prefix = "@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .\n@prefix owl:   <http://www.w3.org/2002/07/owl#> .\n@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
        content = f.read()
        f.seek(0, 0)
        f.write(prefix.rstrip('\r\n') + '\n' + content)
