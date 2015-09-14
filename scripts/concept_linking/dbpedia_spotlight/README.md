DBpedia spotlight performance
=============================

This script measures the entity linking performance of 
DBpedia spotlight against our json datasets using their
REST interface.

To start it, just run 

    python spotlight_performance.py dataset.json dump.json

If you run it for the first time (or use different datasets),
please uncomment the "query_dump()" method in main().
It will create a json dataset from dbpedia to measure the
performance.

For MoviesC-train, the results are:

    :: per-question statistics
    exact match: 90 questions
    partial_match: 270 questions
    not found: 182 questions
    partial or exact match: 66.4206642066% questions
    precision 40.999%, recall 57.472%, F1 45.425%

    :: per-entity statistics
    precision: 406/767, 52.9335071708% 
    recall: 406/721, 56.3106796117% 
    F1 54.570%

