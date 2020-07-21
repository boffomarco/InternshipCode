#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Based on:
# https://www.researchgate.net/publication/272763162_A_Non-Standard_Approach_for_the_OWL_Ontologies_Checking_and_Reasoning

import ontospy
from rdflib import RDFS, OWL


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
    
o = ontospy.Ontospy()

fileName = "people" #, people.owl, Animal.owl, schema_2020-03-10.n3
moduleName = fileName
o.load_rdf("/home/marco/Desktop/Alloy/" + fileName + ".owl")

fileName = "/home/marco/Desktop/Alloy/" + fileName + ".als"

o.build_all()

print(o.stats())

#print(o.all_classes)
#print(o.all_properties)
#print(o.all_shapes)
#print(o.all_ontologies)
#print(o.all_skos_concepts)
#print(o.rdflib_graph)

AlloyModel = ""

for class_ in o.all_classes:
    #print("Class: " + str(class_.uri))
    className = nameOf(class_.uri)

    AlloyClass = "sig " + className

    for subClassOf in class_.parents():
        subClassOfName = nameOf(subClassOf.uri)
        AlloyClass = AlloyClass + " extends " + subClassOfName

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

    AlloyClass = AlloyClass[0:-3] + "} \n"
    
    AlloyModel = AlloyModel + AlloyClass
    #print()

with open(fileName, "w+") as Alloy:
    Alloy.write("module "+ moduleName + "\n\n")
    Alloy.write(AlloyModel)

AlloyModel = ""
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
            if predicateName == "subPropertyOf":       
                subj_range = ""
                if("Property" == str(subj)[1:9] and subj.ranges):
                    print(len(subj.ranges))
                    subj_range = subj.ranges[0].uri
                elif("Class" == str(subj)[1:6] and subj.range_of):
                    print(len(subj.range_of))
                    subj_range = subj.range_of[0].uri            

                AlloyModel = AlloyModel + "// subPropertyOf as Figure4\n"
                AlloyModel = AlloyModel + "pred subPropertyOf{all a:" + nameOf(subj_range) + " | a." + nameOf(subj.uri) + " in a." + nameOf(obj.uri) + "}" + "\n"

                obj_range = ""
                if("Property" == str(obj)[1:9] and obj.ranges):
                    print(len(obj.ranges))
                    obj_range = obj.ranges[0].uri
                elif("Class" == str(obj)[1:6] and obj.range_of):
                    print(len(obj.range_of))
                    obj_range = obj.range_of[0].uri
                
                if(obj_range):
                    AlloyModel = AlloyModel + "// subPropertyOf as TABLE I\n"
                    AlloyModel = AlloyModel + "pred subPropertyOf{all r:" + nameOf(subj_range) + " | r in " + nameOf(obj_range) + "}" + "\n"
                
            elif predicateName == "inverseOf":
                AlloyModel = AlloyModel + "pred inverseOf{" + nameOf(subj.uri) + " = ~" + nameOf(obj.uri) + "}" + "\n"
            
            elif predicateName ==  "disjointWith":
                if(subj.parents() and obj.parents() and subj.parents()[0] != obj.parents()[0]):
                    AlloyModel = AlloyModel + "pred { no c1:" + nameOf(subj.uri) + ", c2:" + nameOf(obj.uri) + "| c1 = c2}" + "\n"
                    
            elif predicateName ==  "complementOf":
                C = "{"
                for class_ in o.all_classes:
                    if(nameOf(obj.uri) != nameOf(class_.uri)):
                        C = C + nameOf(class_.uri)
                C = C + "}"

                AlloyModel = AlloyModel + "pred { " + nameOf(subj.uri) + " = " + str(C) + "}" + "\n"

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