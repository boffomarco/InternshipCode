#! /usr/bin/python3.6
# Import libraries
import rdflib
from rdflib import Graph, Namespace
from rdflib.util import guess_format
from rdflib.plugins.parsers.notation3 import N3Parser


# Mandatory function for RapidMiner
def rm_main():
    # Get the name of the file to serialize
    fileName = ""

    # Try to create the graph to analyze the vocabulary
    try:
        g = Graph()
        format_ = fileName.split(".")[-1]
        if(format_ == "txt"):
            format_ = fileName.split(".")[-2]
        format_ = format_.split("?")[0]
        result = g.parse(fileName, format=guess_format(format_))
    except Exception as e:
        # In case of an error during the graph's initiation, print the error
        print(str(e) + "\n")    

    # Get the formats that will be used for serialization
    strFormats = ""
    dest = fileName.split(".")[0]

    # Serialize the vocabulary in multiple formats
    if("n3" in strFormats.split()):
        g.serialize(destination=dest + ".n3", format="n3")
    if("nt" in strFormats.split()):
        g.serialize(destination=dest + ".nt", format="nt")
    if("rdf" in strFormats.split()):
        g.serialize(destination=dest + ".rdf", format="pretty-xml")
    if("ttl" in strFormats.split()):
        g.serialize(destination=dest + ".ttl", format="turtle")
    if("json" in strFormats.split()):
        g.serialize(destination=dest + ".json-ld", format="json-ld")