#!/bin/sh

export LC_ALL=en_US.utf8

./genquestions.py movies.tsv movies.txt MOVIE 0 | tee q-movies.json

grep 'who is' q-movies.json  | sed -r 's/[^[]*\["//; s/".*//' | sort | uniq >persons.txt
grep 'who is the director' q-movies.json  | sed -r 's/[^[]*\["//; s/".*//' | sort | uniq >directors.txt
grep 'who is the star' q-movies.json  | sed -r 's/[^[]*\["//; s/".*//' | sort | uniq >actors.txt

./genquestions.py persons.tsv persons.txt PERSON 1 | tee q-persons.json
./genquestions.py directors.tsv directors.txt PERSON 2 | tee q-directors.json
./genquestions.py actors.tsv actors.txt PERSON 3 | tee q-actors.json

./genmovch.py movies.txt 4 | tee q-movie-characters.json

# pick every 7-th line to trim things down
n=0
cat q-movies.json q-persons.json q-directors.json q-actors.json q-movie-characters.json |
	while read l; 
	do 
		n=$((n+1)); 
		[ $(((n-1)%7)) != 0 ] || echo "$l"; 
	done > synthetic-.json

# split 3:1 to train:test
rm -f synthetic-train-.json synthetic-test-.json
n=0
cat synthetic-.json | while read l; do
	
	if [ $((n%4)) != 3 ]; then
		echo "$l" >>synthetic-train-.json;
	else
		echo "$l" >>synthetic-test-.json;
	fi
	n=$((n+1))
	done


python ../../yodaqa/data/ml/repair-json.py synthetic-train-.json >synthetic-train.json
python ../../yodaqa/data/ml/repair-json.py synthetic-test-.json >synthetic-test.json
rm synthetic-.json synthetic-train-.json synthetic-test-.json
