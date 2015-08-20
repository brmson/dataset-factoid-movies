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
