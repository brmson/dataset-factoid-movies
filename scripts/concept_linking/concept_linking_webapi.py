#!/usr/bin/pypy
# script for fixing entity linking dataset using web api
# requires a file containing a json array with qId, qText and concepts 
# created by preprocess.py
# usage: python concept_linking_webapi.py concepts_moviesC-train.json output.json
# the output requires some sort of post processing (add square brackets, remove last comma),
# it is not a valid json file
from __future__ import print_function
from flask import *
from SPARQLWrapper import SPARQLWrapper, JSON
app = Flask(__name__)
import sys

concepts_and_questions = {}
output_filename = ""

#loads a file with a json array and creates a corresponding dictionary with qIds as key
def load_from_file(list_filename):
    print("loading concepts")
    concepts_json = json.load(open(list_filename))
    concepts_and_questions = {}
    for jsonobject in concepts_json:
        qId = jsonobject['qId']
        concepts_and_questions[qId] = jsonobject
    print("done")
    return concepts_and_questions

def web_init(list_filename, out_filename):
    global concepts_and_questions
    global output_filename
    output_filename = out_filename
    concepts_and_questions = load_from_file(list_filename)
    app.run(port=5000, host='0.0.0.0', debug=False, use_reloader=False)
#TODO: currently, the address is hardcoded to localhost, change it for web interface?

@app.route('/')
def list_index():
    print ("listing qIds")
    global concepts_and_questions
    output = ""
    for key, value in concepts_and_questions.iteritems():
        output = output + "<a href=http://localhost:5000/"+key+">"+value['qText'] +"</a> <br/>"
    return output

@app.route('/update_concept/<qId>', methods=['POST'])
def update_concept(qId):
    print("saving to file")
    output_file = open(output_filename, "a")
    d = {}
    d['qId'] = qId
    d['qText'] = concepts_and_questions[qId]['qText']
    d['Concept'] = []
    #first, the concepts in from the checkbox
    for concept in request.form.getlist('concept'):
        pageID, label = concept.split(";_;") #custom separator/crying face
        d['Concept'].append({'fullLabel' : label, 'pageID' : pageID})

    #Now the concepts from "unlisted" box
    for extraLabel in request.form.getlist('extraLabel'):
        if extraLabel == "":
            break
        print ("looking for " + extraLabel)
        pageID = retrieve_pageID(extraLabel)
        if pageID == -1:
            #continue to append file? 
            #TODO: add "go back" button 
            return extraLabel +" not found in  http://dbpedia.org/resource/"+extraLabel.replace (" ", "_")+" , please copy the wikipedia label exactly"
        print ("found pageID: " + str(pageID))
        d['Concept'].append({'fullLabel' : extraLabel, 'pageID' : pageID})
    print('  %s,' % (json.dumps(d, sort_keys=True),), file=output_file)
    print(json.dumps(d, sort_keys=False))
    print("done")
    res = "successfully appended " + str(json.dumps(d, sort_keys=False)) + "<br/>"
    res +=  "<p><form method=\"get\" action=\"/\">"
    res += '<p><input type="submit" name="return" value="Return">'
    return res

@app.route('/<qId>')
def process_concept(qId):
    print ("looking for " + qId)
    global concepts_and_questions
    res = concepts_and_questions[qId]
    output = ''
    output += '<p><iframe style="float: right" src="http://en.m.wikipedia.org/" width="640" height="600"></iframe>'
    output += res['qId'] + " : " + res['qText'] + "<br/>"
    output += "<form method=\"post\" action=\"/update_concept/"+qId+"\">"
    for concept in res['Concept']:
        output += '<li><input type="checkbox" name="concept" value="%d;_;%s"> <a href="http://en.wikipedia.org/?curid=%d">%s</a>' % (int(concept['pageID']),concept['fullLabel'], int(concept['pageID']), concept['fullLabel']) + "<br/>" 
    output += '<li>Unlisted: <input type="text" name="extraLabel" value="">'
    for i in range(4):
        output += ' <input type="text" name="extraLabel" value="">'
    output += '<br>(labels exactly as they appear in wikipedia)'
    output += '<p><input type="submit" name="save" value="Save">'
    return output

def retrieve_pageID(label):
    url = 'http://dbpedia.ailao.eu:3030/dbpedia/query'
    sparql = SPARQLWrapper(url)
    sparql.setReturnFormat(JSON)
    sparql_query = '''
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX : <http://dbpedia.org/resource/>
PREFIX dbpedia2: <http://dbpedia.org/property/>
PREFIX dbpedia: <http://dbpedia.org/>
PREFIX dbo: <http://dbpedia.org/ontology/>
SELECT ?pageID ?label ?res WHERE { {
  BIND(<http://dbpedia.org/resource/'''+label.replace (" ", "_")+'''> AS ?res)
} UNION {
  BIND(<http://dbpedia.org/resource/'''+label.replace (" ", "_")+'''> AS ?redir)
  ?redir dbo:wikiPageRedirects ?res .
} UNION {
  BIND(<http://dbpedia.org/resource/'''+label.replace (" ", "_")+'''> AS ?disamb)
  ?disamb dbo:wikiPageDisambiguates ?res .
}
OPTIONAL { ?res dbo:wikiPageRedirects ?redirTarget . }
OPTIONAL { ?res dbo:wikiPageDisambiguates ?disambTarget . }
?res dbo:wikiPageID ?pageID .
?res rdfs:label ?label .
FILTER ( !BOUND(?redirTarget) )
FILTER ( !BOUND(?disambTarget) )
FILTER ( LANG(?label) = 'en' )
 } '''
    sparql.setQuery(sparql_query)
    res = sparql.query().convert()
    print (str(res['results']))
    if len(res['results']) == 0:
        return -1
    return res['results']['bindings'][0]['pageID']['value']

if __name__ == "__main__":
    list_filename = sys.argv[1]
    output_filename = sys.argv[2]
    web_init(list_filename, output_filename)

