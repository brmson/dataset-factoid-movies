Movie QA Benchmarking Dataset
=============================

For one particular application of YodaQA, we want to enhance and speed up
its capability to answer "noisy" questions on a structured knowledge base
in a narrow domain.  To start prototyping, we have chosen the "movies"
domain.

To get started, we extracted movie-related questions from WebQuestions
(http://nlp.stanford.edu/software/sempre/ - Berant et al., 2013, CC-BY)
using the machinery in https://github.com/brmson/dataset-factoid-webquestions
(we use the same JSON structure and scripts in this repo).
This is the **moviesB** dataset.

The **moviesC** dataset also includes "mfb" questions which stand for
"movie feedback", as reported by the YodaQA feedback tool when testing
the YodaQA Movies engine by internet users (mainly interns of the
eClub Prague foundation).  The ``GoogleDocs2json.py`` script extracts
the feedback data from a Google Docs spreadsheet.

We intend to follow up with even larger and better datasets, using
next consecutive letters.

Using with YodaQA
-----------------

YodaQA typically excepts datasets in a TSV format rather than JSON.
(JSON collection reader in YodaQA is work-in-progress.)  To get the
data to TSV format, run

	../dataset-factoid-webquestions/scripts/json2tsv.py moviesC train moviesC
	../dataset-factoid-webquestions/scripts/json2tsv.py moviesC test moviesC

The dataset is called **moviesA** - the A letter represents our intention
to develop it further.  It is currently rather noisy, mixed with sports
questions and not that large either.


**moviesC** is a dataset created by merging the t-movies dataset (here named moviesB for reference) from 
	https://github.com/brmson/dataset-factoid-webquestions/t-movies
and public feedback in our 2 spreadsheets (downloaded 17.8.2015):

	https://docs.google.com/spreadsheets/d/1FELqTPH6EUws5l_qR14igg1aomsKJ8V7iQEKJ5VEefM

	https://docs.google.com/spreadsheets/d/1W43mU78kmp6cSM5JEekdXFm_QM_Brj6piq2vAjG8qNM

**moviesD** is an update of moviesC on 2015-10-19.

**moviesE** is an update of moviesD on 2015-12-10 and inclusion of
synthetic questions gen v0.

**moviesF** is an update of moviesE on 2016-01-04 with a variety of bugs
related to the synthetic questions fixed.

Licence and Acknowledgements
----------------------------

This dataset may be distributed under the terms of the CC-BY 4.0 licence.
Work on this project has been supported in part by the Medialab foundation.
