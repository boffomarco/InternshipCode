#! /usr/bin/python3.6
# Import libraries
import pyupset as pyu
import pandas as pd
import matplotlib.pyplot as plt

import os
from datetime import datetime

tick = datetime.now()

print("Inh...")
# Open the source FCA file
matrix = pd.read_excel(os.path.normpath(os.path.expanduser("~/Desktop/Schermo/OWL_FCA.xlsx")))

# Create the dictionary used to define the UpSetPlot
data_dict = dict()

# Use a set to avoid creating duplicate Columns
typeSet = set()
# Iterate over every row of the matrix
for index, row in matrix.iterrows():
    
    # Get the list of PropertiesTerms of that row
    subjTermList = row["PropertiesTokens"].replace(" -", "").split(" ")
    subjTermList = [x for x in subjTermList if x]
    # Iterate over every Property
    for i in range(0, len(subjTermList)):
        # Save the triple about that Property being a domain of that row Type/Object
        subjTermList[i].replace(" ", "")

    # Add the information of the dataset to the dictionary
    data_dict[row["TypeTerm"]] = pd.DataFrame({'Property':subjTermList})

    print(row["TypeTerm"])
    print(subjTermList)
    print()

tock = datetime.now()   
diff = tock - tick    # the result is a datetime.timedelta object
print(str(diff.total_seconds()) + " seconds") 
print("Plot")
tick = datetime.now()

# Create the UpSet Plot using the given dictionary
pyu.plot(data_dict, unique_keys = ['Property'], sort_by='degree', inters_size_bounds=(10, 20))
# Plot the UpSet Plot 
plt.show(pyu)
#current_figure = plt.gcf()
#current_figure.savefig("test.png")

tock = datetime.now()   
diff = tock - tick    # the result is a datetime.timedelta object
print(str(diff.total_seconds()) + " seconds") 

"""
PLOT THE VOCABULARY AS A GRAPH
import rdflib
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
#from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph
import networkx as nx
import matplotlib.pyplot as plt

url = 'https://lov.linkeddata.es/dataset/lov/vocabs/ocd/versions/2012-04-26.n3'

g = rdflib.Graph()
result = g.parse(url, 'n3')

print(len(result))

G = rdflib_to_networkx_multidigraph(result)
#G = rdflib_to_networkx_graph(result)

# Plot Networkx instance of RDF Graph
pos = nx.spring_layout(G, scale=100)
edge_labels = nx.get_edge_attributes(G, 'r')
nx.draw_networkx_edge_labels(G, pos, labels=edge_labels)
#nx.draw(G)
nx.draw(G, with_labels=True)

plt.show()
"""