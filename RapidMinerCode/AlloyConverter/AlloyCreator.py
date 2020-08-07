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
	#inputFile = "%{inputFile}" #, people.owl, Animal.owl, schema_2020-03-10.n3
	o.load_rdf(inputFile)

	# Create the directory in which store the new vocabulary
	#outputDirectory = "%{outputDirectory}"
	if not os.path.isdir(outputDirectory):
		os.makedirs(outputDirectory)
     
	moduleName = ((str(inputFile).split("/")[-1]).split("."))[-2] + "Creator"
	fileName = outputDirectory + moduleName + ".als"
	
	o.build_all()
	
	print(o.stats())
	
	AlloyModel = "// Classes Definitions \n"
	classes = set() # To avoid duplicates
	for class_ in o.all_classes:
		#print("Class: " + str(class_.uri))
		className = nameOf(class_.uri)
		n = len(classes)
		classes.add(className)
		if(len(classes) > n ):
			AlloyModel = AlloyModel + "sig " + className + " in Class{}\n" #static
	
	AlloyModel = AlloyModel + "\n// Properties Definitions \n"
	properties = set() # To avoid duplicates
	for property_ in o.all_properties:
		#print("Property: " + str(property_.uri))
		property_Name = nameOf(property_.uri)
		n = len(properties)
		properties.add(property_Name)
		if( len(properties) > n ):
			AlloyModel = AlloyModel + "sig " + property_Name + " in Property{}\n" #static

	AlloyDefinitions = ""
	#AlloyDefinitionsFile = "%{AlloyDefinitionsFile}"
	with open(AlloyDefinitionsFile, "r") as AlloyDefinitionsFileRead:
		AlloyDefinitions = AlloyDefinitionsFileRead.read()
		
	with open(fileName, "w+") as Alloy:
	    Alloy.write("module "+ moduleName + "\n\n")
	    
	    Alloy.write(AlloyDefinitions + "\n\n")
	    
	    Alloy.write(AlloyModel)

	AlloyModel = "// From triples' definitions"
	notAlloyModel = ""
	notAlloyPred = set()

	for subject, predicate, object_ in o.rdflib_graph:
		predicateName = nameOf(predicate.encode('utf-8').strip())
		if(predicateName != "type"):
			#print(subject, predicate, object_)
			#print()
		
			subj = o.get_any_entity(uri=subject.encode('utf-8').strip())
			pred = o.get_any_entity(uri=predicate.encode('utf-8').strip())
			obj = o.get_any_entity(uri=object_.encode('utf-8').strip())

			if(subj and obj):
				if predicateName == "subClassOf":       
					AlloyModel = AlloyModel + "fact { subClassOf[" + nameOf(subj.uri) + " , " + nameOf(obj.uri) + " ] }" + "\n"

				elif predicateName == "subPropertyOf":       
					AlloyModel = AlloyModel + "fact { subPropertyOf[" + nameOf(subj.uri) + " , " + nameOf(obj.uri) + " ] }" + "\n"

				elif predicateName == "inverseOf":
					AlloyModel = AlloyModel + "fact { inverseOf[" + nameOf(subj.uri) + " , " + nameOf(obj.uri) + " ] }" + "\n"
				
				elif predicateName ==  "disjointWith":
					AlloyModel = AlloyModel + "fact { disjointWith[" + nameOf(subj.uri) + " , " + nameOf(obj.uri) + " ] }" + "\n"
					
				elif predicateName ==  "domain":
					AlloyModel = AlloyModel + "fact{ domain[ " + nameOf(subj.uri) + " , " + nameOf(obj.uri) + " ] }" + "\n"

				elif predicateName ==  "hasValue":
					AlloyModel = AlloyModel + "fact{ hasValue[ " + nameOf(subj.uri) + " , " + nameOf(obj.uri) + " ] }" + "\n"

				elif predicateName ==  "maxCardinality":
					AlloyModel = AlloyModel + "fact{ maxCardinality[ " + nameOf(subj.uri) + " , " + nameOf(obj.uri) + " ] }" + "\n"

				elif predicateName ==  "allValuesFrom":
					AlloyModel = AlloyModel + "fact{ allValuesFrom[ " + nameOf(subj.uri) + " , " + nameOf(obj.uri) + " ] }" + "\n"

				else:
					notAlloyModel = notAlloyModel + str(subject.encode('utf-8').strip()) + ",\t" + str(predicate.encode('utf-8').strip()) + ",\t" + str(object_.encode('utf-8').strip()) + "\n"
					notAlloyPred.add(str(predicate))
			
			else:
				notAlloyModel = notAlloyModel + str(subject.encode('utf-8').strip()) + ",\t" + str(predicate.encode('utf-8').strip()) + ",\t" + str(object_.encode('utf-8').strip()) + "\n"
				#notAlloyPred.add(str(predicate))
			

	with open(fileName, "a+") as Alloy:
		Alloy.write("\n")
		Alloy.write(AlloyModel)

	with open(fileName+"_notAlloy.csv", "w+") as notAlloy:
		notAlloy.write("List of all the triples not used for Alloy conversion\n")
		notAlloy.write(notAlloyModel)

	with open(fileName+"_notAlloyPredicates.csv", "w+") as notAlloyPredicates:
		notAlloyPredicates.write("List of predicates in valid triples(i.e. those without BlankNodes) not used for Alloy conversion\n")
		for pred in notAlloyPred:
			notAlloyPredicates.write(pred + "\n")


fileName = "Animal" #, people.owl, Animal.owl, schema_2020-03-10.n3
inputFile = "/home/marco/Desktop/Alloy/" + fileName + ".owl"
outputDirectory = "/home/marco/Desktop/Alloy/results/"
AlloyDefinitionsFile = "/home/marco/Desktop/Alloy/AlloyDefinitions.als"

rm_main()