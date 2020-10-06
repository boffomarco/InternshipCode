#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Based on:
# https://www.researchgate.net/publication/272763162_A_Non-Standard_Approach_for_the_OWL_Ontologies_Checking_and_Reasoning
# https://www.researchgate.net/publication/252772655_Model_Generation_in_Description_Logics_What_Can_We_Learn_From_Software_Engineering

import os
import pandas as pd
import ontospy
import re
from rdflib import RDF, RDFS, OWL 


def nameOf(text):
    return (str(text).split("/"))[-1].split("#")[-1]


def domains(property_):
    property_domains = ""
    if(property_.domains):
        for domain_ in property_.domains:
            property_domains = property_domains + str(domain_.uri) + " "
    return property_domains.split()


def ranges(property_):
    property_ranges = ""
    if(property_.ranges):
        for range_ in property_.ranges:
            property_ranges = property_ranges + str(range_.uri) + " "
    return property_ranges.split()



def brackets(complete):
	#print(complete)
	tmp = filter(None, complete.split("(") ) 
	bracketed = ""
	c = 0 # Count level of opened brackets
	for t in tmp: # Iterate over the string to build the original one
		if(c):
			bracketed = bracketed + " ( "
		c = c + 1
		for i in t: # Iterate over every element to identify closed brackets
			if i == ')': # If a bracket is closed then update the opened brackets counter
				c = c - 1 
				if c < 1: # If all the brackets has been closed then return the result
					return bracketed
			bracketed = bracketed + i

	while c > 1: # If there are less closed brackets add the remaining ones
		bracketed = bracketed + " ) "
		c = c - 1 
	return bracketed # Return correctly formatted bracketed result

# Return next expression inside brackets if the first string open a bracket
def nextBrackets(next, complete):
	if("(" in next): 
		return brackets(" ".join(complete))
	else:
		return brackets(next)


#[TODO] Check how to comment redundant Axiom (how to detect and comment) 

def DLAxiomtoAlloy(axiom, level):

	#print(axiom)
	"""
	if(len(axiom.split(" ")) == 1):
		print(axiom)
	"""
	# TBOX
	if("≡" in axiom and level == 0):
		tmp = axiom.split("≡")

		#print(tmp)

		return  "fact { " + DLAxiomtoAlloy( tmp[0] , level + 1) + " = " + DLAxiomtoAlloy( tmp[1] , level + 1) + " }"

	elif("⊑" in axiom and level == 0):
		tmp = axiom.split("⊑")

		#print(tmp)

		return "fact { " + DLAxiomtoAlloy( tmp[0] , level + 1) + " in  ( " + DLAxiomtoAlloy( tmp[1] , level + 1) + " )  }"
	
	if("=" in axiom and level == 0):
		tmp = axiom.split("=")

		#print(tmp)

		return "fact { " + DLAxiomtoAlloy( tmp[0] , level + 1) + " = " + DLAxiomtoAlloy( tmp[1] , level + 1) + " }"

	# (ALC) concept
	elif("⊔" in axiom):
		tmps = axiom.split("⊔")

		#print(tmps)

		final = "  "

		for tmp in tmps:
			final = final + DLAxiomtoAlloy(tmp , level + 1) + " + "

		final = final[0:-2]

		return final

	elif("⊓" in axiom):
		tmps = axiom.split("⊓")

		#print(tmps)

		final = "  "

		for tmp in tmps:
			final = final + DLAxiomtoAlloy(tmp , level + 1) + " & "

		final = final[0:-2]

		return final

	elif("∀" in axiom):
		tmp = axiom.replace('∀', '').split(".")

		#print(tmp)
		
		return " ( univ - ( " + DLAxiomtoAlloy(tmp[0] , level + 1) + ".( univ - " + DLAxiomtoAlloy(nextBrackets(".".join(tmp[1:]).split()[0], ".".join(tmp[1:]).split()) , level + 1) + " ) ) ) "
		
	elif("∃" in axiom):
		tmp = axiom.replace('∃', '')

		#print(tmp)

		return DLAxiomtoAlloy(tmp , level + 1)
		
	elif("¬" in axiom):
		tmp = axiom.split("¬")

		#print(tmp)

		return  "( univ - " + DLAxiomtoAlloy(nextBrackets(tmp[1].split()[0], tmp[1].split()) , level + 1) + " ) "
		
	elif("⁻" in axiom):
		
		#print(axiom)

		for tmp in axiom.split():
			if("⁻" in tmp):

				return "( ~ " + DLAxiomtoAlloy(tmp.replace("⁻", "") , level + 1) + " ) "

	# (SHIQ) concept

	elif("≤" in axiom):
		tmp = axiom.split("≤")

		#print(tmp)

		tmp = tmp[1]

		n = re.findall('\d+',  tmp)[0]

		tmp = tmp.replace(str(n),"")
		
		if("." in tmp):
			tmp = tmp.split(".")

			#print(n)
			#print(tmp)

			return "{ a : univ | #( a.( " + DLAxiomtoAlloy(tmp[0].replace("(","").replace(")","") , level + 1) + " :> " + DLAxiomtoAlloy(tmp[1].replace("(","").replace(")","") , level + 1) + " ) ) <= " + n + "}" 
		
		else:
			return "{ a : univ | #( a.( " + DLAxiomtoAlloy(tmp.replace("(","").replace(")","") , level + 1) + " ) ) <= " + n + "}" 

	elif("≥" in axiom):
		tmp = axiom.split("≥")

		#print(tmp)

		tmp = tmp[1]

		n = re.findall('\d+',  tmp)[0]

		tmp = tmp.replace(str(n),"")
		
		if("." in tmp):
			tmp = tmp.split(".")

			#print(n)
			#print(tmp)

			return "{ a : univ | #( a.( " + DLAxiomtoAlloy(tmp[0].replace("(","").replace(")","") , level + 1) + " :> " + DLAxiomtoAlloy(tmp[1].replace("(","").replace(")","") , level + 1) + " ) ) >= " + n + "}" 
		
		else:
			return "{ a : univ | #( a.( " + DLAxiomtoAlloy(tmp.replace("(","").replace(")","") , level + 1) + " ) ) >= " + n + "}" 

	elif("=" in axiom and level > 0):
		tmp = axiom.split("=")

		#print(tmp)

		tmp = tmp[1]

		n = re.findall('\d+',  tmp)[0]

		tmp = tmp.replace(str(n),"")
		
		if("." in tmp):
			tmp = tmp.split(".")

			#print(n)
			#print(tmp)

			return "{ a : univ | #( a.( " + DLAxiomtoAlloy(tmp[0].replace("(","").replace(")","") , level + 1) + " :> " + DLAxiomtoAlloy(tmp[1].replace("(","").replace(")","") , level + 1) + " ) ) = " + n + "}" 
		
		else:
			return "{ a : univ | #( a.( " + DLAxiomtoAlloy(tmp.replace("(","").replace(")","") , level + 1) + " ) ) = " + n + "}" 
	
	elif("INV." in axiom):
		tmp = axiom.replace("INV.", "~")

		#print(tmp)

		return DLAxiomtoAlloy(tmp , level + 1)


	elif("(" in axiom and ")" in axiom and level == 0):
		tmp = axiom.split("(")
		C = tmp[0].split()[-1]
		tmp = tmp[1].split(")")[0]
		tmp = tmp.split(",")

		if(len(tmp)==1):
			return "fact { " + DLAxiomtoAlloy(tmp[0] , level + 1) + " in " + C + " }"
		elif(len(tmp)==2):
			return "fact { " + DLAxiomtoAlloy(tmp[0] , level + 1) + " -> " + DLAxiomtoAlloy(tmp[1] , level + 1) + " in " + C + " }"
		
		return axiom


	return axiom.replace("(","").replace(")","")


def rm_main(dataDL):

	# Create the directory in which store the new vocabulary
	#outputDirectory = "%{outputDirectory}"
	if not os.path.isdir(outputDirectory):
		os.makedirs(outputDirectory)

	# Define Ontology Analyser	
	o = ontospy.Ontospy()
	# Load Ontology
	#inputFile = "%{inputFile}" #, people.owl, Animal.owl, schema_2020-03-10.n3
	o.load_rdf(inputFile)
	o.build_all()
     
	moduleName = ((str(inputFile).split("/")[-1]).split("."))[-2] + "DL"
	fileName = outputDirectory + moduleName + ".als"
	
	AlloyModel = "module " + moduleName + "\n\n"

	usedProperties = set()
	usedDataTypes = set()

	AlloySignatures = "// Specific Signatures\n"

	# Add Classes & Properties to Alloy
	for class_ in o.all_classes:
		#print("Class: " + str(class_.uri))
		className = nameOf(class_.uri)

		AlloyClass = "sig " + className + " in TOP "

		AlloyClass = AlloyClass + " { \n\t"

		for property_ in o.all_properties:
			#print("Property: " + str(property_.uri))
			domains_ = domains(property_)
			if(len(domains_) == 1):
				property_Name = nameOf(property_.uri)
				for domain_ in domains_:
					if(domain_ == str(class_.uri)):
						#print("Domain: " + str(domain_))
						ranges_ = ranges(property_)
						if(len(ranges_) == 1):
							#print("Range: " + str(range_))
							rangeName = nameOf(ranges_[0])
							AlloyClass = AlloyClass + property_Name + ": set " + rangeName + ",\n\t"
							usedProperties.add(property_)
							usedDataTypes.add(rangeName)
						else:
							AlloyClass = AlloyClass + property_Name + ": set TOP,\n\t"
							usedProperties.add(property_)
							
					#print()
			#print()
		AlloyClass = AlloyClass[0:-3] + "} \n"
		
		AlloySignatures = AlloySignatures + AlloyClass
		#print()


 	# Define TOP with remaining properties
	AlloyModel = AlloyModel + "// General Signatures\n"
	AlloyModel = AlloyModel + "abstract sig TOP { \n"

	for property_ in o.all_properties:
		property_Name = nameOf(property_.uri)
		if(property_ not in usedProperties):
			# Don't take into account AnnotationProperties of OWL
			if (property_.uri, RDF.type, OWL.AnnotationProperty) not in o.rdflib_graph:

				ranges_ = ranges(property_)
				if(len(ranges_) == 1):
					rangeName = nameOf(ranges_[0])
					if(rangeName == "Thing"):
						rangeName = "TOP"
					AlloyModel = AlloyModel + "\t" + property_Name + ": set " + rangeName + ",\n"
					usedDataTypes.add(rangeName)
				else:
					AlloyModel = AlloyModel + "\t" + property_Name + ": set TOP,\n"

	AlloyModel = AlloyModel[0:-2] + "}\n"

	AlloyModel = AlloyModel + "sig BOTTOM in TOP {} fact { #BOTTOM = 0 } \n\n"

	unUsedProperties = set(o.all_properties) - usedProperties
	unUsedPropertiesLabels = set()
	for uUP in unUsedProperties:
		unUsedPropertiesLabels.add(nameOf(uUP.uri))

	"""
	# To add if we want to keep also class relations
	validLabels = unUsedPropertiesLabels
	for validClass in o.all_classes:
		validLabels.add(nameOf(validClass.uri))
	"""

	AlloyAxioms = "\n// Axioms\n"
	AlloyAxiomsComment = "\n// Non Relevant Axioms\n"

	# Iterate for every DL Axioms
	for index, row in dataDL.iterrows():

		if (row["DLAxioms"]):

			axioms = row["DLAxioms"].encode('utf-8').strip()

			# Split across multiple axioms on same row
			for axiom in axioms.split(","):
				AlloyAxiom = axiom
				if("⊤" in axiom):
					checkAxiomRange = axiom.split(".⊤")[0].split(" ")[-1]
					rangeReplacement = "TOP"
					for property_ in o.all_properties:
						property_Name = nameOf(property_.uri)
						if(property_Name == checkAxiomRange):
							ranges_ = ranges(property_)
							if(len(ranges_) == 1):
								rangeReplacement = nameOf(ranges_[0])
								if(rangeReplacement == "Thing"):
									rangeReplacement = "TOP"
					AlloyAxiom = DLAxiomtoAlloy(axiom.replace("⊤", rangeReplacement).replace(",", ""), 0)

				if (AlloyAxiom[0] == "{"):
					print(AlloyAxiom)
					AlloyAxiom = "fact " + AlloyAxiom
				#print(AlloyAxiom)
				
				if("fact {" in AlloyAxiom[0:6]):
					comment = "// "
					for label in unUsedPropertiesLabels:
						if(label in AlloyAxiom):
							comment = ""
					if(comment):
						AlloyAxiomsComment = AlloyAxiomsComment + comment + AlloyAxiom + "\n"
					else:
						AlloyAxioms = AlloyAxioms + comment + AlloyAxiom + "\n"
					
				#print("")

	AlloyProperties = "\n// Properties\n"

	for subject, predicate, object_ in o.rdflib_graph:
		#print(subject, predicate, object_)
		#print()
		
		predicateName = nameOf(predicate.encode('utf-8').strip())
		
		subj = o.get_any_entity(uri=subject.encode('utf-8').strip())
		pred = o.get_any_entity(uri=predicate.encode('utf-8').strip())
		obj = o.get_any_entity(uri=object_.encode('utf-8').strip())

		# PREDICATE MAPPING FROM OWL TO ALLOY
		if(subj and obj and predicateName != "type"):
			
			if predicateName == "subPropertyOf":       
				subj_range = ""
				if("Property" == str(subj)[1:9] and subj.ranges):
					#print(len(subj.ranges))
					subj_range = subj.ranges[0].uri
				elif("Class" == str(subj)[1:6] and subj.range_of):
					#print(len(subj.range_of))
					subj_range = subj.range_of[0].uri            

				if(nameOf(subj_range) and nameOf(subj.uri) and nameOf(obj.uri)):
					AlloyProperties = AlloyProperties + "fact {all a:" + nameOf(subj_range) + " | a." + nameOf(subj.uri) + " in a." + nameOf(obj.uri) + "} // subPropertyOf as Figure4\n"

				obj_range = ""
				if("Property" == str(obj)[1:9] and obj.ranges):
					#print(len(obj.ranges))
					obj_range = obj.ranges[0].uri
				elif("Class" == str(obj)[1:6] and obj.range_of):
					#print(len(obj.range_of))
					obj_range = obj.range_of[0].uri
				
				if(nameOf(subj_range) and nameOf(obj_range)):
					obj_range = nameOf(obj_range)
					if(obj_range == "Thing"):
						obj_range = "TOP"
					AlloyProperties = AlloyProperties + "fact {all r:" + nameOf(subj_range) + " | r in " + obj_range + "} // subPropertyOf as TABLE I\n"
				
			elif predicateName == "inverseOf":
				AlloyProperties = AlloyProperties + "fact {" + nameOf(subj.uri) + " = ~" + nameOf(obj.uri) + "} // inverseOf\n"
			
			elif predicateName ==  "disjointWith":
				if(subj.parents() and obj.parents() and subj.parents()[0] != obj.parents()[0]):
					AlloyProperties = AlloyProperties + "fact { no c1:" + nameOf(subj.uri) + ", c2:" + nameOf(obj.uri) + "| c1 = c2} // disjointWith\n"
					
			elif predicateName ==  "complementOf":
				C = "{"
				for class_ in o.all_classes:
					if(nameOf(obj.uri) != nameOf(class_.uri)):
						C = C + nameOf(class_.uri)
				C = C + "}"

				AlloyProperties = AlloyProperties + "fact { " + nameOf(subj.uri) + " = " + str(C) + "} // complementOf\n"

			elif predicateName ==  "equivalentClass":
				AlloyProperties = AlloyProperties + "fact { " + nameOf(subj.uri) + " = " + nameOf(obj.uri) + "} // equivalentClass\n"

			elif predicateName ==  "equivalentProperty":
				AlloyProperties = AlloyProperties + "fact { " + nameOf(subj.uri) + " = " + nameOf(obj.uri) + "} // equivalentProperty\n"

			elif predicateName ==  "TransitiveProperty":
				AlloyProperties = AlloyProperties + "fact { a,b,c ∈ " + nameOf(subj.uri) + " / a.(" + nameOf(predicate) + ") = b && b.(" + nameOf(predicate) + ") = c ⇒ a.(" + nameOf(predicate) + ") = c } // TransitiveProperty\n"

			elif predicateName ==  "hasValue":
				if(("Property" == str(pred)[1:9] and pred.ranges) or ("Class" == str(pred)[1:6] and pred.range_of)):
					pred_range = nameOf(pred.ranges[0])
					if(pred_range == "Thing"):
						pred_range = "TOP"
					AlloyProperties = AlloyProperties + "fact { #( " + pred_range + " ) = 1} // hasValue\n"

			elif predicateName ==  "cardinality":
				if(("Property" == str(pred)[1:9] and pred.ranges) or ("Class" == str(pred)[1:6] and pred.range_of)):
					pred_range = nameOf(pred.ranges[0])
					if(pred_range == "Thing"):
						pred_range = "TOP"
					AlloyProperties = AlloyProperties + "fact { #( " + pred_range + " ) = " + nameOf(obj.uri) + "} // cardinality\n"

			elif predicateName ==  "maxCardinality":
				if(("Property" == str(pred)[1:9] and pred.ranges) or ("Class" == str(pred)[1:6] and pred.range_of)):
					pred_range = nameOf(pred.ranges[0])
					if(pred_range == "Thing"):
						pred_range = "TOP"
					AlloyProperties = AlloyProperties + "fact { #( " + pred_range + " ) <= " + nameOf(obj.uri) + "} // maxCardinality\n"

			elif predicateName ==  "minCardinality":
				if(("Property" == str(pred)[1:9] and pred.ranges) or ("Class" == str(pred)[1:6] and pred.range_of)):
					pred_range = nameOf(pred.ranges[0])
					if(pred_range == "Thing"):
						pred_range = "TOP"
					AlloyProperties = AlloyProperties + "fact { #( " + pred_range + " ) >= " + nameOf(obj.uri) + "} // minCardinality\n"

			elif predicateName ==  "SymmetricProperty":
				if((("Property" == str(pred)[1:9] and pred.ranges) or ("Class" == str(pred)[1:6] and pred.range_of)) and (("Property" == str(pred)[1:9] and pred.domains) or ("Class" == str(pred)[1:6] and pred.domain_of))):
					AlloyProperties = AlloyProperties + "fact { a ∈ " + pred.domains[0] + " &&  b ∈ " + pred.ranges[0] + " / a.(" + nameOf(predicate) + ")  = b ⇒ b.(" + nameOf(predicate) + ") } // SymmetricProperty\n"

			elif predicateName ==  "FunctionalProperty":
				if(("Property" == str(pred)[1:9] and pred.ranges) or ("Class" == str(pred)[1:6] and pred.range_of)):
					pred_range = nameOf(pred.ranges[0])
					if(pred_range == "Thing"):
						pred_range = "TOP"
					AlloyProperties = AlloyProperties + "fact { #(" + pred_range + ") = 1} //FunctionalProperty \n"

			elif predicateName ==  "InverseFunctionalProperty":
				if(("Property" == str(pred)[1:9] and pred.domains) or ("Class" == str(pred)[1:6] and pred.domain_of)):
					AlloyProperties = AlloyProperties + "fact { #(" + pred.domains[0] + ") = 1} // InverseFunctionalProperty\n"

			elif predicateName ==  "allValuesFrom":
				if(("Property" == str(pred)[1:9] and pred.ranges) or ("Class" == str(pred)[1:6] and pred.range_of)):
					pred_range = nameOf(pred.ranges[0])
					if(pred_range == "Thing"):
						pred_range = "TOP"
					AlloyProperties = AlloyProperties + "fact { " + pred_range + " in " + nameOf(obj.uri) + "} // allValuesFrom\n"

			elif predicateName ==  "someValuesFrom":
				if(("Property" == str(pred)[1:9] and pred.ranges) or ("Class" == str(pred)[1:6] and pred.range_of)):
					pred_range = nameOf(pred.ranges[0])
					if(pred_range == "Thing"):
						pred_range = "TOP"
					AlloyProperties = AlloyProperties + "fact { some r: " + pred_range + " | r in " + nameOf(obj.uri) + "} // someValuesFrom\n"

		# META-PROPERTY OF OWL TO ALLOY
		elif(predicateName == "type"):
			
			if(nameOf(object_) == "FunctionalObjectProperty"):
				if("Property" == str(subj)[1:9] and subj.ranges):
					#print(len(subj.ranges))
					subj_range = subj.ranges[0].uri
					if(subj_range == "Thing"):
						subj_range = "TOP"
				AlloyProperties = AlloyProperties + "fact { all c: " + subj_range + "| lone " + nameOf(subject)+ ".c } // FunctionalObjectProperty \n"

			elif(nameOf(object_) == "InverseFunctionalProperty"):
				if("Property" == str(subj)[1:9] and subj.domains):
					#print(len(subj.domains))
					subj_domain = subj.domains[0].uri
				AlloyProperties = AlloyProperties + "fact { all c: " + subj_domain + "| lone c." + nameOf(subject)+ " } // InverseFunctionalProperty \n"

			elif(nameOf(object_) == "TransitiveProperty"):
				AlloyProperties = AlloyProperties + "fact { " + nameOf(subj.uri) + "." + nameOf(subj.uri) + " in " + nameOf(subj.uri) + " } // TransitiveProperty \n"

			elif(nameOf(object_) == "SymmetricProperty"):
				AlloyProperties = AlloyProperties + "fact { ~" + nameOf(subj.uri) + " in " + nameOf(subj.uri) + " } // SymmetricProperty \n"

			elif(nameOf(object_) == "AsymmetricProperty"):
				AlloyProperties = AlloyProperties + "fact {~" + nameOf(subj.uri) + "  & " + nameOf(subj.uri) + " in iden} // AsymmetricProperty \n"

			elif(nameOf(object_) == "ReflexiveProperty"):
				if("Property" == str(subj)[1:9] and subj.domains):
					#print(len(subj.domains))
					subj_domain = subj.domains[0].uri
				AlloyProperties = AlloyProperties + "fact {" + subj_domain + "<:iden in " + nameOf(subj.uri) + "} // ReflexiveProperty \n"

			elif(nameOf(object_) == "IrreflexiveProperty"):
				AlloyProperties = AlloyProperties + "fact {no iden & " + nameOf(subj.uri) + "} // IrreflexiveProperty \n"


	with open(fileName, "w+") as Alloy:
		Alloy.write(AlloyModel)

		Alloy.write(AlloySignatures)

		Alloy.write(AlloyProperties)

		Alloy.write(AlloyAxioms)

		Alloy.write(AlloyAxiomsComment)


	# Comment unUsed DataTypes
	AlloyUtils = ""
	#AlloyUtilsFile = "%{AlloyUtilsFile}"
	with open(AlloyUtilsFile, "r") as AlloyUtilsFileRead:
		if("TOP" in usedDataTypes):
			usedDataTypes.remove("TOP")
		for line in AlloyUtilsFileRead.readlines():
			if(len(line) > 1 and line[0:2] != "//"):
				comment = "// "
				for datatype in usedDataTypes:
					if(datatype in line):
						comment = ""
				AlloyUtils = AlloyUtils + comment + line.strip() + "\n"
			else:
				AlloyUtils = AlloyUtils + line.strip() + "\n"

	with open(fileName, "a+") as Alloy:
		Alloy.write("\n")
		Alloy.write(AlloyUtils)

	#print(AlloyModel)



AlloyUtilsFile = "/home/marco/Desktop/Alloy/AlloyUtils.als"
fileName = "gufo" #, people.owl, Animal.owl, schema_2020-03-10.n3
inputFile = "/home/marco/Desktop/Alloy/" + fileName + ".owl"
outputDirectory = "/home/marco/Desktop/Alloy/results/"

inputFile = "/home/marco/Desktop/Alloy/InputCheck/yes.owl"
outputDirectory = "/home/marco/Desktop/Alloy/InputCheck/results/"


#test = pd.read_excel("/home/marco/Desktop/Alloy/peopleDL_.xlsx")
#test = pd.read_excel("/home/marco/Desktop/Alloy/gufoDL.xlsx")
test = pd.read_excel("/home/marco/Desktop/Alloy/InputCheck/yesDL.xls")

rm_main(test)

#print(DLAxiomtoAlloy("∃ partitions.⊤ ⊑ (Type ⊓ (¬AbstractIndividualType) ⊓ (¬ConcreteIndividualType))",0))
#print(DLAxiomtoAlloy("Interrogation ⊑ = 1 ContributesTo.CrimeInvestigation",0))
#print(DLAxiomtoAlloy("Interrogation ⊑ ≤ 1 ContributesTo.CrimeInvestigation",0))

#print(DLAxiomtoAlloy("Aspect = ExtrinsicAspect ⊔ IntrinsicAspect",0))
#print(DLAxiomtoAlloy("Aspect = ExtrinsicAspect ⊔ IntrinsicAspect  ⊔ safsasadda",0))
#print(DLAxiomtoAlloy("ExtrinsicAspect ⊑ ¬ IntrinsicAspect",0))
#print(DLAxiomtoAlloy("ExtrinsicAspect ⊑ ¬ IntrinsicAspect  ⊔ safsasadda",0))

#print(DLAxiomtoAlloy("⊤ ⊑ ¬∃ externallyDependsOn .self",0))

#print(DLAxiomtoAlloy("∃ partitions.⊤ ⊑ (Type ⊓ (¬AbstractIndividualType) ⊓ (¬ConcreteIndividualType))",0,set(["partitions"])))