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
import urllib

fburl = 'http://freebase.ailao.eu:3030/freebase/query'
dbpurl = 'http://dbpedia.ailao.eu:3030/dbpedia/query'
labelurl = 'http://pasky.or.cz:5001/'

def queryWikipediaLabel(name):
    response = urllib.request.urlopen(labelurl + 'search/' + urllib.parse.quote(name))
    jsonres = response.read().decode('utf8')
    res = json.loads(jsonres)
    return res['results'][0]['name'] if res['results'] else None

def queryWikipediaIdRedirected(label):
    if label is None: return None
    sparql = SPARQLWrapper(dbpurl)
    sparql.setReturnFormat(JSON)
    sparql_query = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?pageID WHERE { 
<http://dbpedia.org/resource/''' + label + '''> <http://dbpedia.org/ontology/wikiPageRedirects> ?tgt .
?tgt <http://dbpedia.org/ontology/wikiPageID> ?pageID .
} '''
    sparql.setQuery(sparql_query)
    res = sparql.query().convert()
    retVal = []
    for r in res['results']['bindings']:
        retVal.append(r['pageID']['value'])
    return retVal[0] if retVal else None

def queryWikipediaId(label):
    if label is None: return None
    # first, check if this is a redirect and traverse it
    retVal = queryWikipediaIdRedirected(label)
    if retVal is not None:
        return retVal
    sparql = SPARQLWrapper(dbpurl)
    sparql.setReturnFormat(JSON)
    sparql_query = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?pageID WHERE { 
<http://dbpedia.org/resource/''' + label + '''> <http://dbpedia.org/ontology/wikiPageID> ?pageID .
} '''
    sparql.setQuery(sparql_query)
    res = sparql.query().convert()
    retVal = []
    for r in res['results']['bindings']:
        retVal.append(r['pageID']['value'])
    return retVal[0] if retVal else None

def queryFreebaseKey(pageID):
    if pageID is None: return None
    sparql = SPARQLWrapper(fburl)
    sparql.setReturnFormat(JSON)
    sparql_query = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://rdf.freebase.com/ns/>
SELECT DISTINCT ?topic WHERE { 
?topic <http://rdf.freebase.com/key/wikipedia.en_id> "''' + pageID + '''" .
} '''
    sparql.setQuery(sparql_query)
    res = sparql.query().convert()
    retVal = []
    for r in res['results']['bindings']:
        retVal.append(r['topic']['value'])
    return retVal[0] if retVal else None

def queryAnswer(query):
    sparql = SPARQLWrapper(fburl)
    sparql.setReturnFormat(JSON)
    sparql_query = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://rdf.freebase.com/ns/>
SELECT DISTINCT ?ans WHERE {
''' + query + '''
OPTIONAL { ?a rdfs:label ?alabel . FILTER(LANG(?alabel) = "en") }
BIND(IF(BOUND(?alabel), ?alabel, ?a) AS ?ans)
}'''
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
    if '$' in query or '$' in qText:
        print('Unsubstituted variable: '+qText, file=sys.stderr)
        return
    answers = queryAnswer(query)
    if not answers:
        print('No answer (skipping): '+qText, file=sys.stderr)
        return

    qid = 'syn%02d%04d' % (int(sys.argv[4]), n)
    print('{ "qId": "%s", "qText": "%s", "answers": [%s], "tags": ["%s"] }' % (qid, qText, ', '.join(['"'+a+'"' for a in answers]), q.tag))

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
            ents = el.split(';')
            labels = sys.argv[3].split(',')
            edict = dict()
            for i in range(len(labels)):
                fbkey = queryFreebaseKey(queryWikipediaId(queryWikipediaLabel(ents[i])))
                print('%s: %s' % (ents[i], fbkey), file=sys.stderr)
                if not fbkey:
                    continue
                edict[labels[i]] = (ents[i], fbkey)
            # print(edict)
            entities.append(edict)

    n = 0
    for edict in entities:
        print('... ' + ', '.join(edict.keys()), file=sys.stderr)
        for q in questions:
            genquestion(n, q, edict)
            n += 1
