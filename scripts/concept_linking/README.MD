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
might not find anything if you put in extra spaces and 
nonunicode characters.

To create your own dataset, you can use preprocess.py.
It requires the data from yodaQA questionDump and the 
original dataset.

to run it:

	python preprocess.py questionDump.json originalDataset.json concepts_Dataset.json

The result is appended to output.json. The output file 
is not a valid json, it requires postprocessing:

You can use the postprocessing script like this:

    python postprocess.py dataset_from_webapi.json train.json output.json

The script creates a valid json, checks for missing/duplicate
entries and sorts it. You can run the functions separately.

The concept_linking_performance.py script takes the fixed 
QuestionDump json and the sorted dataset and measures the
performance. 

    python concept_linking_performance.py questionDump.json correct_dataset.json

It prints the number of exact matches, recall (when there
is atleast one match) and incorrect concepts.