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
