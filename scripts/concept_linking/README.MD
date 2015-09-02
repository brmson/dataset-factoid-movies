Concept linking webapi
======================

This script runs a python Flask server to create a entity 
linking dataset. It requires a file containing a 
json array with qId, qText and a list of concepts.
We included one, concepts_moviesC-train.json, created
from moviesC-train dataset.

To start this script, run:

	python concept_linking_webapi.py concepts_moviesC-train.json output.json

The web itself is at localhost:5000/, there is a list of 
questions. When you click on one, you can choose the
correct concepts. The labels link to the corresponding
wikipedia entries for easy checking. If a concept is 
missing, you can search it in the wikipedia box to the
right. Then copy the label to the "unlisted" text boxes. 
The system will try to find the pageID in dbpedia, so it
might not find anything if you put in extra spaces and such.

The result is appended to output.json. The output file 
is not a valid json, it requires postprocessing:
* add square brackets 
* remove last comma

The postprocessing script will be added later.

To create your own dataset, you can use preprocess.py.
It requires the data from yodaQA questionDump and the 
original dataset.

to run it:

	python preprocess.py questionDump.json originalDataset.json concepts_Dataset.json
	

