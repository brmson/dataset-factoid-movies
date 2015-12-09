#!/usr/bin/python3 -u
#
# Generate questions from a given set of templates
#
# Example: genquestions.py movie-characters.tsv movie-characters.txt MOVIE,CHARACTER,PERSON 0
#
# ...where 0 is the "generation" number for the synthetic generator
# so that on re-runs with new templates, question IDs are not reused.

from collections import namedtuple
from SPARQLWrapper import SPARQLWrapper, JSON
import json, sys

url = 'http://freebase.ailao.eu:3030/freebase/query'

def queryFreebaseKey(label):
    sparql = SPARQLWrapper(url)
    sparql.setReturnFormat(JSON)
    sparql_query = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://rdf.freebase.com/ns/>
SELECT DISTINCT ?topic WHERE { 
?topic rdfs:label "''' + label + '''"@en .
} '''
    sparql.setQuery(sparql_query)
    res = sparql.query().convert()
    retVal = []
    for r in res['results']['bindings']:
        retVal.append(r['topic']['value'])
    return retVal[0]

def queryAnswer(query):
    sparql = SPARQLWrapper(url)
    sparql.setReturnFormat(JSON)
    sparql_query = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://rdf.freebase.com/ns/>
SELECT DISTINCT ?ans WHERE {
''' + query + '''
OPTIONAL { ?a rdfs:label ?alabel . FILTER(LANG(?alabel) = "en") }
BIND(IF(BOUND(?alabel), ?alabel, ?a) AS ?ans)
}'''
    # print(sparql_query)
    sparql.setQuery(sparql_query)
    res = sparql.query().convert()
    retVal = []
    for r in res['results']['bindings']:
        retVal.append(r['ans']['value'])
    # print('RV', retVal)
    return retVal

def genquestion(n, q, edict):
    qText = q.qText
    query = q.query
    for elabel, entity in edict.items():
        entname, enturl = entity
        qText = qText.replace('$'+elabel, entname)
        query = query.replace('$'+elabel, '<'+enturl+'>')
    answers = queryAnswer(query)
    if not answers:
        print('No answer (skipping): '+qText, file=sys.stderr)
        return

    qid = 'syn%02d%04d' % (int(sys.argv[4]), n)
    print('%s\t%s\t%s\t%s' % (qid, qText, '|'.join(answers), q.tag))

Question = namedtuple("Question", "qText query tag")


if __name__ == "__main__":
    questions = []
    with open(sys.argv[1], 'r') as qf:
        for ql in qf:
            ql = ql.rstrip('\n')
            if ql == '':
                continue
            tag, qText, query = ql.split('\t')
            if query == 'TODO':
                print('skipping TODO question: ' + qText, file=sys.stderr)
                continue
            questions.append(Question(qText, query, tag))

    entities = []
    with open(sys.argv[2], 'r') as ef:
        for el in ef:
            el = el.rstrip('\n')
            ents = el.split(',')
            labels = sys.argv[3].split(',')
            edict = dict()
            for i in range(len(labels)):
                edict[labels[i]] = (ents[i], queryFreebaseKey(ents[i]))
            # print(edict)
            entities.append(edict)

    n = 0
    for edict in entities:
        for q in questions:
            genquestion(n, q, edict)
            n += 1
