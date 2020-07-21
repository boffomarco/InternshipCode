#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Based on:
# https://www.researchgate.net/publication/220535396_Reasoning_support_for_Semantic_Web_ontology_family_languages_using_Alloy

import ontospy
from rdflib import RDFS, OWL


def nameOf(text):
    return (str(text).split("/"))[-1].split("#")[-1]
    
o = ontospy.Ontospy()

fileName = "people" #, people.owl, Animal.owl, schema_2020-03-10.n3
moduleName = fileName
o.load_rdf("/home/marco/Desktop/Alloy/" + fileName + ".owl")

fileName = "/home/marco/Desktop/Alloy/" + fileName + ".als"

o.build_all()

print(o.stats())

AlloyModel = ""

for class_ in o.all_classes:
    #print("Class: " + str(class_.uri))
    className = nameOf(class_.uri)
    AlloyModel = AlloyModel + "sig " + className + " in Class{}\n" #static

AlloyModel = AlloyModel + "\n"

for property_ in o.all_properties:
    #print("Property: " + str(property_.uri))
    property_Name = nameOf(property_.uri)
    AlloyModel = AlloyModel + "sig " + property_Name + " in Property{}\n" #static


with open(fileName, "w+") as Alloy:
    Alloy.write("module "+ moduleName + "\n\n")
    
    Alloy.write("sig Resource {} \n\n")
    #Alloy.write("disj sig Property extends Resource \n {sub_val: Resource -> Resource}\n\n")
    Alloy.write("sig Property extends Resource \n {sub_val: Resource -> Resource}\n\n")
    #Alloy.write("disj sig Class extends Resource {instances: set Resource}\n\n")
    Alloy.write("sig Class extends Resource {instances: set Resource}\n\n")
    Alloy.write("sig Datatype extends Class {}\n\n")

    Alloy.write("sig List {} \n" + \
                "sig NonEmptyList extends List {next: List, element: Resource} \n" + \
                "fact Canonical { \n" + \
                "\tno disj p0, p1: List | p0.next = p1.next and p0.element = p1.element \n" + \
                "} \n" + \
                "fun List::first (): Resource {this.element} \n" + \
                "fun List::rest (): List {this.next} \n" + \
                "fun List::addFront (e: Resource): List { \n" + \
                "\t{p: List | p.next = this and p.element = e} \n" + \
                "}\n\n")

    Alloy.write("fun subClassOf [csup, csub: Class] : Class \n {csub.instances in csup.instances}\n\n")
    Alloy.write("fun disjointWith [c1, c2: Class] : Class {no c1.instances & c2.instances}\n\n")
    Alloy.write("fun allValuesFrom \n [p: Property, c1: Class, c2: Class] : Resource \n {all r1, r2: Resource | \n r1 in c1.instances => \n r2 in r1.(p.sub_val) => \n r2 in c2.instances}\n\n")
    Alloy.write("fun hasValue [p: Property, c1: Class, r: Resource] : Resource \n {all r1: Resource | r1 in c1.instances => r1.(p.sub_val) = r}\n\n")
    Alloy.write("fun maxCardinality [p: Property, c1: Class, N: Int] : Resource \n {all r1: Resource| r1 in c1.instances <=> \n # r1.(p.sub_val) <= int N }\n\n")
    Alloy.write("fun intersectionOf [clist: List, c1: Class] : Resource \n {all r: Resource| r in c1.instances <=> \n all ca: clist.*next.val | r in ca.instances}\n\n")
    Alloy.write("fun unionOf [clist: List, c1: Class] : Resource \n {all r: Resource| r in c1.instances <=> \n some ca: clist.*next.val| r in ca.instances}\n\n")
    
    Alloy.write("fun subPropertyOf [psup, psub: Property] : Property \n {psub.sub_val in psup.sub_val}\n\n")
    Alloy.write("fun domain [p: Property, c: Class] : Resource \n {(p.sub_val).Resource in c.instances}\n\n")
    Alloy.write("fun inverseOf [p1, p2: Property] : Property {p1.sub_val = ~(p2.sub_val)} \n\n")

    Alloy.write(AlloyModel)