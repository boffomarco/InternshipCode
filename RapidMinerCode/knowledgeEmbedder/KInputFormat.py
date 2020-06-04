# Import libraries
import pandas as pd
from random import random
import os

# Mandatory function for RapidMiner
def rm_main(triples):

	# Create Directory if not already present
	if not os.path.isdir("%{ResultDirectory}/%{DatasetFinalName}"):
		os.makedirs("%{ResultDirectory}/%{DatasetFinalName}")

	# Create output files
	with open(r"%{FolderPath}/%{DatasetFinalName}.tsv", "w+") as train:
		# Iterate over every triples row
		for index, row in triples.iterrows():
			train.write(str(row["Subject"])+"\t"+str(row["Predicate"])+"\t"+str(row["Object"])+"\n") 	
			
	return 