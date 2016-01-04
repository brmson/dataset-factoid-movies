#!/usr/bin/python3 -u
#
# Generate movie-character questions from a given set of movies
#
# Example: genmovch.py movies.txt 4
#
# ...where 4 is the "generation" number for the synthetic generator
# so that on re-runs with new templates, question IDs are not reused.

from __future__ import print_function

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

def queryMovieCharacter(movie):
    sparql = SPARQLWrapper(fburl)
    sparql.setReturnFormat(JSON)
    sparql_query = '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns: <http://rdf.freebase.com/ns/>
SELECT ?p ?q WHERE {
<''' + movie + '''> ns:film.film.starring ?s .
?s ns:film.performance.actor ?pp .
?pp rdfs:label ?p .
?s ns:film.performance.character ?qq .
?qq rdfs:label ?q .
FILTER(LANG(?p) = "en") FILTER(LANG(?q) = "en")
} LIMIT 4'''
    sparql.setQuery(sparql_query)
    res = sparql.query().convert()
    retVal = []
    for r in res['results']['bindings']:
        retVal.append((r['p']['value'], r['q']['value']))
    # print('RV', retVal)
    return retVal

def genquestion(n, edict):
    if not 'MOVIE' in edict:
        return n
    answers = queryMovieCharacter(edict['MOVIE'][1])

    for actor, character in answers:
        for i, qText, ans in [
                    (n, 'Who played '+character+' in '+edict['MOVIE'][0]+'?', actor),
                    (n+1, 'Who did '+actor+' play in '+edict['MOVIE'][0]+'?', character),
                ]:
            qid = 'syn%02d%04d' % (int(sys.argv[2]), i)
            print('{ "qId": "%s", "qText": "%s", "answers": [%s], "Concept": [{"fullLabel": "%s", "pageID": "%s"}], "tags": ["%s"] }' % \
                (qid, qText, '"'+ans+'"', edict['MOVIE'][0],edict['MOVIE'][2], "cvt"))
        n += 2
    return n


if __name__ == "__main__":
    entities = []
    with open(sys.argv[1], 'r') as ef:
        for el in ef:
            el = el.rstrip('\n')
            ents = el.split(';')
            labels = ['MOVIE']
            edict = dict()
            for i in range(len(labels)):
                wiki_id = queryWikipediaId(queryWikipediaLabel(ents[i]))
                fbkey = queryFreebaseKey(wiki_id)
                print('%s: %s (%s)' % (ents[i], fbkey, wiki_id), file=sys.stderr)
                if not fbkey:
                    continue
                edict[labels[i]] = (ents[i], fbkey, wiki_id)
            # print(edict)
            entities.append(edict)

    n = 0
    for edict in entities:
        #print('... ' + ', '.join(edict.keys()), file=sys.stderr)
        n = genquestion(n, edict)
