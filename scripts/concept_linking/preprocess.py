#!/usr/bin/pypy
# takes the concept dump, the original dataset and creates a new dataset containing qId, question text and concepts
# usage: python preprocess.py questionDump_moviesC-train.json moviesC-train.json concepts_moviesC-train.json

from __future__ import print_function
import sys
import json

#extracts from questionDump and dataset
def extract():
    argv = sys.argv
    concepts_filename = argv[1]
    questions_filename = argv[2]
    output_filename = argv[3]
    concepts_json = json.load(open(concepts_filename))
    questions_json = json.load(open(questions_filename))
    output = open(output_filename,"w")
    number_of_questions = len(concepts_json)
    
    print('[', file=output)
    question_counter = 0
    print (str(number_of_questions) +  " questions")
    while question_counter < number_of_questions:
        currentID = concepts_json[question_counter]['qId']
        if currentID != questions_json[question_counter]['qId']:
            print("ID's are not equal, exiting")
            break
        d = {}
        d['qId'] = currentID
        d['qText'] = questions_json[question_counter]['qText']
        d['Concept'] = []
        for concept in concepts_json[question_counter]['Concept']:
            d['Concept'].append({'fullLabel' : concept['fullLabel'], 'pageID' : concept['pageID']})
        if question_counter < number_of_questions-1:
            print('  %s,' % (json.dumps(d, sort_keys=True),), file=output)
        else:
            print('  %s' % (json.dumps(d, sort_keys=True),), file=output)
        question_counter = question_counter + 1
    print(']', file=output)

if __name__ == "__main__": extract()