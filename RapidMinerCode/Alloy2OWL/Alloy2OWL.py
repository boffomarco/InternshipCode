#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os import listdir
from os.path import isfile, join
import pandas as pd
import ontospy
import re


import rdflib
from rdflib import Graph, Literal, RDFS, RDF, OWL, Namespace, URIRef
from rdflib.util import guess_format
from rdflib.plugins.parsers.notation3 import N3Parser



def nameOf(text):
    return (str(text).split("/"))[-1].split("#")[-1]


# Return identifier of the Alloy and related instances
def scrapeLine(line):
	if("this" in line):
		instances = line.split("{")[1].split("}")[0]
		if(instances):
			identifier = line.split("=")[0].split("/")[-1].split(":")[-1]
			if(identifier == "TOP" or identifier == "Individual"):
				return "", ""
			#print(instances + " " + identifier)
			return instances, identifier
	return "", ""


def rm_main():

	# Create the directory in which store the new vocabulary
	#outputDirectory = "%{outputDirectory}"
	outputDirectory = "/home/marco/Desktop/Alloy/Converter/"
	if not os.path.isdir(outputDirectory):
		os.makedirs(outputDirectory)

	# Get inputFile name to generate graph
	#inputFile = "%{inputFile}" #, people.owl, Animal.owl, schema_2020-03-10.n3
	inputFile = "/home/marco/Desktop/Alloy/Converter/investigation.v00.owl"

	# Try to create the graph to analyze the vocabulary
	try:
		g = Graph()
		format_ = inputFile.split(".")[-1]
		if(format_ == "txt"):
			format_ = inputFile.split(".")[-2]
		format_ = format_.split("?")[0]
		result = g.parse(inputFile, format=guess_format(format_))
	except Exception as e:
		# In case of an error during the graph's initiation, print the error and return an empty list
		print(str(e) + "\n")    
		return -1

	# Define Ontology Analyser	
	o = ontospy.Ontospy()
	# Load Ontology
	o.load_rdf(inputFile)
	o.build_all()

	# Get original namespace
	originalURI = str(o.namespaces[0][1])
	nmspc = Namespace(originalURI)

	# Add Classes
	classDict = dict()
	for class_ in o.all_classes:
		#print("Class: " + str(class_.uri))
		className = nameOf(class_.uri)
		classDict[className] = class_.uri
	# Add Proprieties
	propertyDict = dict()
	for property_ in o.all_properties:
		#print("Property: " + str(property_.uri))
		propertyName = nameOf(property_.uri)
		propertyDict[propertyName] = property_.uri

	index = 0
	#inputDirectory = "%{inputDirectory}"

	inputDirectory = "/home/marco/Desktop/Alloy/Converter/"

	AlloyFiles = [join(inputDirectory, f) for f in listdir(inputDirectory) if ( (isfile(join(inputDirectory, f))) and (".txt" in f[-4:]) )]
	print(AlloyFiles)
	for AlloyResult in AlloyFiles:
		with open(AlloyResult) as Alloy:
			data = Alloy.readlines()
			
			for line in data:
				
				instances, identifier = scrapeLine(line)
				#print(line)
				for instance in instances.replace(" ","").split(","):
					if(instance and identifier):
						#print(identifier + " " + instance)
						#print()
						
						if("->" in instance):
							relation = instance.replace("->", ",").split(",")
							print(nmspc[relation[0] + "!" + str(index)] + " " + propertyDict[identifier] + " " + nmspc[relation[1] + "!" + str(index)])
							o.rdflib_graph.add((nmspc[relation[0] + "!" + str(index)], propertyDict[identifier], nmspc[relation[1] + "!" + str(index)]))
						else:
							print(nmspc[instance + "!" + str(index)] + " " + RDF.type + " " + classDict[identifier] )
							o.rdflib_graph.add((nmspc[instance + "!" + str(index)], RDF.type, classDict[identifier]))
						
		index = index + 1
	#AlloyResult = "%{AlloyResult}"
	#index = AlloyResult.split(".")[0][-1]
	
	o.rdflib_graph.serialize(destination=str(os.path.join(outputDirectory, inputFile.split("/")[-1].split(".")[0] + ".ttl")), format="turtle")



#AlloyResult = "/home/marco/Desktop/Alloy/A2O/simulation0.txt"
fileName = "people" #, people.owl, Animal.owl, schema_2020-03-10.n3, gufo.owl
inputFile = "/home/marco/Desktop/Alloy/" + fileName + ".owl"
inputFile = "/home/marco/Desktop/Alloy/A2O/people.n3"
#inputFile = "/home/marco/Desktop/Alloy/Converter/investigation.v00.owl"
#outputDirectory = "/home/marco/Desktop/Alloy/Converter/"

#inputDirectory = "/home/marco/Desktop/Alloy/Converter/"


rm_main()

