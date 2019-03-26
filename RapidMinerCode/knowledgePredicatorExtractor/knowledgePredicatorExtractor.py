import pandas as pd
import os
import time
import re

# Logs the date with the string str to track errors 
def log(name_, str_):
	ts = time.strftime("%Y-%m-%d %H:%M:%S - ", time.gmtime())
	f = open(name_, "a+")
	str_ = str_.encode("utf-8")
	f.write(ts + str(str_) + "\n")
	f.close()

# Mandatory function for RapidMiner
def rm_main():
	# Create the folder used to store the results
	location = os.path.normpath(os.path.expanduser("~/Desktop/K-Files/"))

	# Create the DataFrame to save the LOVs' vocabs' information
	#df = pd.DataFrame(columns=["prefix", "Type", "Property", "Predicate"])

	# Add information for each file of the directory
	set_ = set()
	dict_ = dict()
	for fileName in os.listdir(location):
		if("_Filtered_" in fileName):
			log("log.txt","Reading  : " + fileName)
			vocabs = pd.read_excel(os.path.join(location, fileName))
			log("log.txt","Filtering: " + fileName)
			# Iterate for every vocabulary read from the second argument
			for index_, row in vocabs.iterrows():
				a = len(set_)
				set_.add(row["Predicate"])
				if(a < len(set_)):
					#log("SubjPredObj.txt",str(row["Subject"])+"     "+str(row["Predicate"])+"      "+str(row["Object"]))
					dict_[row["Predicate"]] = {"number": 1, "Subject": str(row["Subject"]), "Predicate": str(row["Predicate"]), "Object": str(row["Object"])}
				else:
					n = dict_[row["Predicate"]]
					n = n["number"]
					dict_.update({row["Predicate"]: {"number": n+1, "Subject": str(row["Subject"]), "Predicate": str(row["Predicate"]), "Object": str(row["Object"])}})
			"""
			# Create the list used to contain the information about the other vocabularies
			list_ = list()
			index = 0
			# Iterate for every vocabulary read from the Excel file
			for index, row in vocabs.iterrows():
				# Add the vocabulary to the list
				list_.insert(index,{"prefix": row["prefix"], "Type": row["Object"], "Property": row["Subject"], "Predicate": row["Predicate"]})
				# Update the index for the next element of the list
				index += 1
			# Add the list of that Excel file to the DataFrame, if there are vocabularies in that Excel file
			if(len(list_)):
				df = df.append(list_, ignore_index=True)"""
	log("occurrencesEx.txt", str(dict_))

rm_main()