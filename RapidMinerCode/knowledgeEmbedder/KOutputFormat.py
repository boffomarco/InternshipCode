# Import libraries
import pandas as pd
import json
import numpy as np


# Mandatory function for RapidMiner
def rm_main():
	# Directory with the results of the Embedder
	#output_directory="%{ResultDirectory}"
	output_directory="/home/marco/Documents/Internship/resources/Vocabularies/schema_R/pyKEENres"

	# Retrieve Entities Embedding from json file
	with open(output_directory+'/entities_to_embeddings.json') as entitiesE:
		entitiesEJSON = json.load(entitiesE)

	# Set the DataFrame that will contain the EuclideanNorm of evry combination of entities
	entitiesDF = pd.DataFrame({"Entities|Entities": list(entitiesEJSON.keys())})
	entitiesDF["Entities|Entities"] = range(0, len(entitiesEJSON.keys()))
	# Initiate it at 0.0 for every entry
	for i in range(0, len(entitiesEJSON.keys())):
		entitiesDF[i] = 0.0

	# Iterate over every cell of the DataFrame
	for i in range(0, len(entitiesEJSON.keys())):
		for j in range(0, len(entitiesEJSON.keys())):
			# Work only with elements not on the diagonal and not already checked 
			if(i != j and entitiesDF.iat[i,j+1] == 0.0):
				# Transform the embeddings into a numpy array
				arrayI = np.array(entitiesEJSON[list(entitiesEJSON.keys())[i]])
				arrayJ = np.array(entitiesEJSON[list(entitiesEJSON.keys())[j]])
				# Compute the Euclidean norm between these 2 arrays
				norm = np.linalg.norm(arrayI - arrayJ)
				# Update both the combinations with the norm
				entitiesDF.iat[i,j+1] = str(norm)
				entitiesDF.iat[j,i+1] = str(norm)

	# Store the DataFrame as a csv file
	entitiesDF.to_csv(output_directory+'/entitiesMatrix.csv', index=False)


	# Retrieve Entities ID from json file
	with open(output_directory+'/entity_to_id.json') as entitiesID:
		entitiesIDJSON = json.load(entitiesID)
		entitiesIDJSON = list(entitiesIDJSON.keys())


	# Store top 10 closest Entities as a Json file Object
	with open(output_directory+'/entitiesList.json', 'w+') as entitiesL:
		# Start the Json object
		entitiesL.write("{\n")

		# Iterate over each Entity
		for i in range(0, len(entitiesDF.columns)-1):
			# If it's the first, skip the initial comma, for a correct Json formatting
			if(i):
				entitiesL.write(",")

			# Start Entity entry list
			entitiesL.write("\""+entitiesIDJSON[i]+"\":[\n")
			# Order the Entities DataFrame by that Entity
			entitiesDF.sort_values(by=[i], inplace=True)
			# Iterate over the top 10 closest Entities
			for j in range(1, 11):
				# If it's the first, skip the initial comma, for a correct Json formatting
				if(j!=1):
					entitiesL.write(",")
				# Add the close Entity together with its distance norm
				entitiesL.write(str("[\"" + str(entitiesIDJSON[entitiesDF.iloc[j,0]]) + "\"," +  str(entitiesDF.iloc[j,i+1]) + "]\n").encode('utf-8').decode("utf-8"))
			# End that Entity list
			entitiesL.write("]\n")

		# End the Json object
		entitiesL.write("}")


	# Retrieve Relations Embedding from json file
	with open(output_directory+'/relations_to_embeddings.json') as relationsE:
		relationsEJSON = json.load(relationsE)
	
	# Set the DataFrame that will contain the EuclideanNorm of every combination of relations
	relationsDF = pd.DataFrame({"Relations|Relations":  list(relationsEJSON.keys())})
	# Initiate it at 0.0 for every entry
	for relKey in relationsEJSON.keys():
		relationsDF[relKey] = 0.0

	# Iterate over every cell of the DataFrame
	for i in range(0, len(relationsEJSON.keys())):
		for j in range(0, len(relationsEJSON.keys())):
			# Work only with elements not on the diagonal and not already checked
			if(i != j and relationsDF.iat[i,j+1] == 0.0):
				# Transform the embeddings into a numpy array
				arrayI = np.array(relationsEJSON[list(relationsEJSON.keys())[i]])
				arrayJ = np.array(relationsEJSON[list(relationsEJSON.keys())[j]])
				# Compute the Euclidean norm between these 2 arrays
				norm = np.linalg.norm(arrayI - arrayJ)
				# Update both the combination with the norm
				relationsDF.iat[i,j+1] = norm
				relationsDF.iat[j,i+1] = norm

	# Store the DataFrame as a csv file
	relationsDF.to_csv(output_directory+'/relationsMatrix.csv')


	# Store top 5 closest Relations as a Json file Object
	with open(output_directory+'/relationsList.json', 'w+') as relationsL:
		# Start the Json object
		relationsL.write("{\n")

		# Iterate over every Relation
		i = 1
		for relation in relationsDF.columns[1:]:
			# If it's the first, skip the initial comma, for a correct Json formatting
			if(i!=1):
				relationsL.write(",")

			# Start Relation entry list
			relationsL.write("\""+relation+"\":[\n")
			# Order the Relation DataFrame by that Relation
			relationsDF.sort_values(by=[relation], inplace=True)
			for j in range(0, 5):
				# Iterate over the top 5 closest Relations
				if(j!=0):
					relationsL.write(",")
				# Add the close Relation together with its distance norm
				relationsL.write(str("[\"" + str(relationsDF.iloc[j,0]) + "\"," +  str(relationsDF.iloc[j,i]) + "]\n").encode('utf-8').decode("utf-8"))
			# End that Relation list
			relationsL.write("]\n")

			# Update the index
			i += 1

		# End the Json object
		relationsL.write("}")

	# Return the DataFrames to RapidMiner for visualization
	return entitiesDF, relationsDF


rm_main()