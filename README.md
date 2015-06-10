Movie QA Benchmarking Dataset
=============================

For one particular application of YodaQA, we want to enhance and speed up
its capability to answer "noisy" questions on a structured knowledge base
in a narrow domain.  To start prototyping, we have chosen the "movies"
domain, with movie-related questions from the WebQuestions dataset
(http://nlp.stanford.edu/software/sempre/ - Berant et al., 2013, CC-BY)
meant to be answerable using IMDB.

More documentation to come.  The data here has been extracted using

	bzcat ../yodaqa/data/eval/webquestions.examples.train.json.bz2 | egrep 'utterance.*play|star[^t]|voice|movie|\bact' | egrep -v 'play[^ ]* (for|4)\b|position|playoff|soccer|music|sport|ball|guitar|tennis' | tee moviesA-train.json | ./json2tsv.pl wqmAr >moviesA-train.tsv
	bzcat ../yodaqa/data/eval/webquestions.examples.test.json.bz2 | egrep 'utterance.*play|star[^t]|voice|movie|\bact' | egrep -v 'play[^ ]* (for|4)\b|position|playoff|soccer|music|sport|ball|guitar|tennis' | tee moviesA-test.json | ./json2tsv.pl wqmAs >moviesA-test.tsv

The dataset is called **moviesA** - the A letter represents our intention
to develop it further.  It is currently rather noisy, mixed with sports
questions and not that large either.
