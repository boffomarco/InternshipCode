#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Based on:
# https://www.researchgate.net/publication/272763162_A_Non-Standard_Approach_for_the_OWL_Ontologies_Checking_and_Reasoning
# https://www.researchgate.net/publication/252772655_Model_Generation_in_Description_Logics_What_Can_We_Learn_From_Software_Engineering

import os
import pandas as pd
import ontospy
import re


def nameOf(text):
    return (str(text).split("/"))[-1].split("#")[-1]


def domains(property_):
    property_domains = ""
    if(property_.domains):
        for domain_ in property_.domains:
            property_domains = property_domains + str(domain_.uri) + " "
    elif(property_.parents()):
        for property_parent in property_.parents():
            property_domains = property_domains + " " + " ".join(domains(property_parent))
    return property_domains.split()


def ranges(property_):
    property_ranges = ""
    if(property_.ranges):
        for range_ in property_.ranges:
            property_ranges = property_ranges + str(range_.uri) + " "
    elif(property_.parents()):
        for property_parent in property_.parents():
            property_ranges = property_ranges + " " + " ".join(ranges(property_parent))
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



def DLAxiomtoAlloy(axiom, level):

	#print(axiom)

	# TBOX
	if("≡" in axiom):
		tmp = axiom.split("≡")

		#print(tmp)

		return "fact { " + DLAxiomtoAlloy( tmp[0] , level + 1 ) + " = " + DLAxiomtoAlloy( tmp[1] , level + 1 ) + " }"

	elif("⊑" in axiom):
		tmp = axiom.split("⊑")

		#print(tmp)

		return "fact { " + DLAxiomtoAlloy( tmp[0] , level + 1 ) + " in  ( " + DLAxiomtoAlloy( tmp[1] , level + 1 ) + " )  }"
	
	if("=" in axiom and level == 0):
		tmp = axiom.split("=")

		#print(tmp)

		return "fact { " + DLAxiomtoAlloy( tmp[0] , level + 1 ) + " = " + DLAxiomtoAlloy( tmp[1] , level + 1 ) + " }"

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

			return "{ a : univ | #( a.( " + DLAxiomtoAlloy(tmp[0].replace("(","").replace(")","") , level + 1) + " :> " + DLAxiomtoAlloy(tmp[1].replace("(","").replace(")","") , level + 1) + " ) ) =< " + n + "}" 
		
		else:
			return "{ a : univ | #( a.( " + DLAxiomtoAlloy(tmp.replace("(","").replace(")","") , level + 1) + " ) ) =< " + n + "}" 

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

			return "{ a : univ | #( a.( " + DLAxiomtoAlloy(tmp[0].replace("(","").replace(")","") , level + 1) + " :> " + DLAxiomtoAlloy(tmp[1].replace("(","").replace(")","") , level + 1) + " ) ) => " + n + "}" 
		
		else:
			return "{ a : univ | #( a.( " + DLAxiomtoAlloy(tmp.replace("(","").replace(")","") , level + 1) + " ) ) => " + n + "}" 

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
		return axiom#"fact { " + DLAxiomtoAlloy(tmp[0] , level + 1) + " -> " + DLAxiomtoAlloy(tmp[1] , level + 1) + " in " + C + " }"


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

	AlloySignatures = "\n// Signatures\n"

	# Add Classes & Properties to Alloy
	for class_ in o.all_classes:
		#print("Class: " + str(class_.uri))
		className = nameOf(class_.uri)

		AlloyClass = "sig " + className + " in TOP "

		"""
		for subClassOf in class_.parents():
			subClassOfName = nameOf(subClassOf.uri)
			AlloyClass = AlloyClass + " extends " + subClassOfName
		"""
		AlloyClass = AlloyClass + " { \n\t"

		for property_ in o.all_properties:
			#print("Property: " + str(property_.uri))
			domains_ = domains(property_)
			property_Name = nameOf(property_.uri)
			for domain_ in domains_:
				if(domain_ == str(class_.uri)):
					#print("Domain: " + str(domain_))
					ranges_ = ranges(property_)
					for range_ in ranges_:
						#print("Range: " + str(range_))
						AlloyClass = AlloyClass + property_Name + ": " + nameOf(range_) + ",\n\t"
						usedProperties.add(property_Name)

		AlloyClass = AlloyClass[0:-3] + "} \n"
		
		AlloySignatures = AlloySignatures + AlloyClass
		#print()


	AlloyModel = AlloyModel + "abstract sig TOP { \n"

	for property_ in o.all_properties:
		property_Name = nameOf(property_.uri)
		if(property_Name not in usedProperties):
			#print(property_Name)
			AlloyModel = AlloyModel + property_Name + " : set TOP,\n"

	AlloyModel = AlloyModel[0:-2] + "}\n"
	AlloyModel = AlloyModel + "sig BOTTOM in TOP {} fact { #BOTTOM = 0 } \n\n"


	AlloyAxioms = "\n// Axioms\n"

	# Iterate for every DL Axioms
	for index, row in dataDL.iterrows():

		if (row["DLAxioms"]):
			axiom = row["DLAxioms"].encode('utf-8').strip()

			AlloyAxiom = DLAxiomtoAlloy(axiom.replace("⊤", "TOP").replace(",", ""), 0)

			if (AlloyAxiom[0] == "{"):
				AlloyAxiom = "fact  " + AlloyAxiom
			#print(AlloyAxiom)
			
			if("fact {" in AlloyAxiom[0:6]):
				AlloyAxioms = AlloyAxioms + AlloyAxiom + "\n"
			#print("")

	AlloyPredicates = "\n// Predicates\n"

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

				AlloyModel = AlloyModel + "// subPropertyOf as Figure4\n"
				if(nameOf(subj_range) and nameOf(subj.uri) and nameOf(obj.uri)):
					AlloyModel = AlloyModel + "pred subPropertyOf{all a:" + nameOf(subj_range) + " | a." + nameOf(subj.uri) + " in a." + nameOf(obj.uri) + "}" + "\n"

				obj_range = ""
				if("Property" == str(obj)[1:9] and obj.ranges):
					#print(len(obj.ranges))
					obj_range = obj.ranges[0].uri
				elif("Class" == str(obj)[1:6] and obj.range_of):
					#print(len(obj.range_of))
					obj_range = obj.range_of[0].uri
				
				if(nameOf(subj_range) and nameOf(obj_range)):
					AlloyModel = AlloyModel + "// subPropertyOf as TABLE I\n"
					AlloyModel = AlloyModel + "pred subPropertyOf{all r:" + nameOf(subj_range) + " | r in " + nameOf(obj_range) + "}" + "\n"
				
			elif predicateName == "inverseOf":
				AlloyModel = AlloyModel + "pred inverseOf{" + nameOf(subj.uri) + " = ~" + nameOf(obj.uri) + "}" + "\n"
			
			elif predicateName ==  "disjointWith":
				if(subj.parents() and obj.parents() and subj.parents()[0] != obj.parents()[0]):
					AlloyModel = AlloyModel + "pred { no c1:" + nameOf(subj.uri) + ", c2:" + nameOf(obj.uri) + "| c1 = c2} // disjointWith \n"
					
			elif predicateName ==  "complementOf":
				C = "{"
				for class_ in o.all_classes:
					if(nameOf(obj.uri) != nameOf(class_.uri)):
						C = C + nameOf(class_.uri)
				C = C + "}"

				AlloyModel = AlloyModel + "pred { " + nameOf(subj.uri) + " = " + str(C) + "} // complementOf \n"

			elif predicateName ==  "equivalentClass":
				AlloyModel = AlloyModel + "pred equivalentClass{ " + nameOf(subj.uri) + " = " + nameOf(obj.uri) + "}" + "\n"

			elif predicateName ==  "equivalentProperty":
				AlloyModel = AlloyModel + "pred equivalentProperty{ " + nameOf(subj.uri) + " = " + nameOf(obj.uri) + "}" + "\n"

			elif predicateName ==  "TransitiveProperty":
				AlloyModel = AlloyModel + "pred TransitiveProperty{ a,b,c ∈ " + nameOf(subj.uri) + " / a.(" + nameOf(predicate) + ") = b && b.(" + nameOf(predicate) + ") = c ⇒ a.(" + nameOf(predicate) + ") = c }" + "\n"

			elif predicateName ==  "hasValue":
				if(("Property" == str(pred)[1:9] and pred.ranges) or ("Class" == str(pred)[1:6] and pred.range_of)):
					AlloyModel = AlloyModel + "pred hasValue{ #( " + pred.ranges[0] + " ) = 1}" + "\n"

			elif predicateName ==  "cardinality":
				if(("Property" == str(pred)[1:9] and pred.ranges) or ("Class" == str(pred)[1:6] and pred.range_of)):
					AlloyModel = AlloyModel + "pred cardinality{ #( " + pred.ranges[0] + " ) = " + nameOf(obj.uri) + "}" + "\n"

			elif predicateName ==  "maxCardinality":
				if(("Property" == str(pred)[1:9] and pred.ranges) or ("Class" == str(pred)[1:6] and pred.range_of)):
					AlloyModel = AlloyModel + "pred maxCardinality{ #( " + pred.ranges[0] + " ) <= " + nameOf(obj.uri) + "}" + "\n"

			elif predicateName ==  "minCardinality":
				if(("Property" == str(pred)[1:9] and pred.ranges) or ("Class" == str(pred)[1:6] and pred.range_of)):
					AlloyModel = AlloyModel + "pred minCardinality{ #( " + pred.ranges[0] + " ) >= " + nameOf(obj.uri) + "}" + "\n"

			elif predicateName ==  "SymmetricProperty":
				if((("Property" == str(pred)[1:9] and pred.ranges) or ("Class" == str(pred)[1:6] and pred.range_of)) and (("Property" == str(pred)[1:9] and pred.domains) or ("Class" == str(pred)[1:6] and pred.domain_of))):
					AlloyModel = AlloyModel + "pred SymmetricProperty{ a ∈ " + pred.domains[0] + " &&  b ∈ " + pred.ranges[0] + " / a.(" + nameOf(predicate) + ")  = b ⇒ b.(" + nameOf(predicate) + ") }" + "\n"

			elif predicateName ==  "FunctionalProperty":
				if(("Property" == str(pred)[1:9] and pred.ranges) or ("Class" == str(pred)[1:6] and pred.range_of)):
					AlloyModel = AlloyModel + "pred FunctionalProperty{ #(" + pred.ranges[0] + ") = 1}" + "\n"

			elif predicateName ==  "InverseFunctionalProperty":
				if(("Property" == str(pred)[1:9] and pred.domains) or ("Class" == str(pred)[1:6] and pred.domain_of)):
					AlloyModel = AlloyModel + "pred InverseFunctionalProperty{ #(" + pred.domains[0] + ") = 1}" + "\n"

			elif predicateName ==  "allValuesFrom":
				if(("Property" == str(pred)[1:9] and pred.ranges) or ("Class" == str(pred)[1:6] and pred.range_of)):
					AlloyModel = AlloyModel + "pred allValuesFrom{ " + nameOf(pred.ranges[0]) + " in " + nameOf(obj.uri) + "}" + "\n"

			elif predicateName ==  "someValuesFrom":
				if(("Property" == str(pred)[1:9] and pred.ranges) or ("Class" == str(pred)[1:6] and pred.range_of)):
					AlloyModel = AlloyModel + "pred allValuesFrom{ some r: " + nameOf(pred.ranges[0]) + " | r in " + nameOf(obj.uri) + "}" + "\n"

		# META-PROPERTY OF OWL TO ALLOY
		elif(predicateName == "type"):
			
			if(nameOf(object_) == "FunctionalObjectProperty"):
				if("Property" == str(subj)[1:9] and subj.ranges):
					#print(len(subj.ranges))
					subj_range = subj.ranges[0].uri
				AlloyModel = AlloyModel + "fact { all c: " + subj_range + "| lone " + nameOf(subject)+ ".c } // FunctionalObjectProperty \n"

			elif(nameOf(object_) == "InverseFunctionalProperty"):
				if("Property" == str(subj)[1:9] and subj.domains):
					#print(len(subj.domains))
					subj_domain = subj.domains[0].uri
				AlloyModel = AlloyModel + "fact { all c: " + subj_domain + "| lone c." + nameOf(subject)+ " } // InverseFunctionalProperty \n"

			elif(nameOf(object_) == "TransitiveProperty"):
				AlloyModel = AlloyModel + "fact { " + nameOf(subj.uri) + "." + nameOf(subj.uri) + " in " + nameOf(subj.uri) + " } // TransitiveProperty \n"

			elif(nameOf(object_) == "SymmetricProperty"):
				AlloyModel = AlloyModel + "fact { ~" + nameOf(subj.uri) + " in " + nameOf(subj.uri) + " } // SymmetricProperty \n"

			elif(nameOf(object_) == "AsymmetricProperty"):
				AlloyModel = AlloyModel + "fact {~" + nameOf(subj.uri) + "  & " + nameOf(subj.uri) + " in iden} // AsymmetricProperty \n"

			elif(nameOf(object_) == "ReflexiveProperty"):
				if("Property" == str(subj)[1:9] and subj.domains):
					#print(len(subj.domains))
					subj_domain = subj.domains[0].uri
				AlloyModel = AlloyModel + "fact {" + subj_domain + "<:iden in " + nameOf(subj.uri) + "} // ReflexiveProperty \n"

			elif(nameOf(object_) == "IrreflexiveProperty"):
				AlloyModel = AlloyModel + "fact {no iden & " + nameOf(subj.uri) + "} // IrreflexiveProperty \n"


	with open(fileName, "w+") as Alloy:
		Alloy.write(AlloyModel)

		Alloy.write(AlloySignatures)

		Alloy.write(AlloyAxioms)

		Alloy.write(AlloyPredicates)


	AlloyUtils = ""
	#AlloyUtilsFile = "%{AlloyUtilsFile}"
	with open(AlloyUtilsFile, "r") as AlloyUtilsFileRead:
		AlloyUtils = AlloyUtilsFileRead.read()

	with open(fileName, "a+") as Alloy:
		Alloy.write("\n")
		Alloy.write(AlloyUtils)

	#print(AlloyModel)



AlloyUtilsFile = "/home/marco/Desktop/Alloy/AlloyUtils.als"
fileName = "gufo" #, people.owl, Animal.owl, schema_2020-03-10.n3
inputFile = "/home/marco/Desktop/Alloy/" + fileName + ".owl"
outputDirectory = "/home/marco/Desktop/Alloy/results/"

inputFile = "/home/marco/Desktop/Alloy/InputCheck/no.owl"
outputDirectory = "/home/marco/Desktop/Alloy/InputCheck/results/"


#test = pd.read_excel("/home/marco/Desktop/Alloy/peopleDL_.xlsx")
#test = pd.read_excel("/home/marco/Desktop/Alloy/gufoDL.xlsx")
test = pd.read_excel("/home/marco/Desktop/Alloy/InputCheck/noDL.xls")

rm_main(test)

#print(DLAxiomtoAlloy("∃ partitions.⊤ ⊑ (Type ⊓ (¬AbstractIndividualType) ⊓ (¬ConcreteIndividualType))",0))
#print(DLAxiomtoAlloy("Interrogation ⊑ = 1 ContributesTo.CrimeInvestigation",0))
#print(DLAxiomtoAlloy("Interrogation ⊑ ≤ 1 ContributesTo.CrimeInvestigation",0))

#print(DLAxiomtoAlloy("Aspect = ExtrinsicAspect ⊔ IntrinsicAspect",0))
#print(DLAxiomtoAlloy("Aspect = ExtrinsicAspect ⊔ IntrinsicAspect  ⊔ safsasadda",0))
#print(DLAxiomtoAlloy("ExtrinsicAspect ⊑ ¬ IntrinsicAspect",0))
#print(DLAxiomtoAlloy("ExtrinsicAspect ⊑ ¬ IntrinsicAspect  ⊔ safsasadda",0))

#print(DLAxiomtoAlloy("⊤ ⊑ ¬∃ externallyDependsOn .self",0))





