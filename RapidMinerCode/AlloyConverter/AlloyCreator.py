#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Based on:
# https://www.researchgate.net/publication/220535396_Reasoning_support_for_Semantic_Web_ontology_family_languages_using_Alloy

import ontospy
import os
from rdflib import RDFS, OWL

def nameOf(text):
    return (str(text).split("/"))[-1].split("#")[-1]

def rm_main():
	# Define Ontology Analyser	
	o = ontospy.Ontospy()
	AlloyDefinitions = ""
	inputFile = "%{inputFile}" #, people.owl, Animal.owl, schema_2020-03-10.n3
	o.load_rdf(inputFile)

	# Create the directory in which store the new vocabulary
	outputDirectory = "%{outputDirectory}"
	if not os.path.isdir(outputDirectory):
		os.makedirs(outputDirectory)
     
	moduleName = ((str(inputFile).split("/")[-1]).split("."))[-2] + "Creator"
	fileName = outputDirectory + moduleName + ".als"
	
	o.build_all()
	
	print(o.stats())
	
	AlloyModel = "// Classes Definitions \n"
	
	for class_ in o.all_classes:
	    #print("Class: " + str(class_.uri))
	    className = nameOf(class_.uri)
	    AlloyModel = AlloyModel + "sig " + className + " in Class{}\n" #static
	
	AlloyModel = AlloyModel + "\n// Properties Definitions \n"
	
	for property_ in o.all_properties:
	    #print("Property: " + str(property_.uri))
	    property_Name = nameOf(property_.uri)
	    AlloyModel = AlloyModel + "sig " + property_Name + " in Property{}\n" #static

	AlloyDefinitions = ""
	with open("%{AlloyDefinitions}", "r") as AlloyDefinitionsFile:
		AlloyDefinitions = AlloyDefinitionsFile.read()
		
	with open(fileName, "w+") as Alloy:
	    Alloy.write("module "+ moduleName + "\n\n")
	    
	    Alloy.write(AlloyDefinitions + "\n\n")
	    
	    Alloy.write(AlloyModel)

	return str("module "+ moduleName + "\n\n" + AlloyDefinitions + "\n\n" + AlloyModel)