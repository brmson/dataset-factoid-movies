#!/usr/bin/pypy
# Script to measure dbpedia spotlight performance on our JSON datasets
# To measure the performance, you first need a query dump from dbpedia
# To do that, just uncomment the "query_dump()" method in main
# Usage:
# python spotlight_performance.py dataset.json dump.json


import pycurl
import sys
import urllib
import json
import time
from StringIO import StringIO


def query(question):
    reload(sys)
    sys.setdefaultencoding("ISO-8859-1")
    encoded_question = "text=" + urllib.quote_plus(question, "?")
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, "http://spotlight.dbpedia.org/rest/annotate/")
    c.setopt(c.USERAGENT, "Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20121202 Firefox/17.0 Iceweasel/17.0.1")
    c.setopt(c.HTTPHEADER, ["confidence=0.5", "Accept:application/json"])
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, encoded_question)
    c.perform()
    c.close()
    contents = buffer.getvalue()
    return contents


def query_dump(qlist, output_filename):
    output = open(output_filename, "w")
    output.write('[\n')
    number_of_questions = len(qlist)
    question_counter = 0
    for question in qlist:
        res = json.loads(query(question['qText']))
        time.sleep(1)
        print res
        d = {}
        d['qId'] = question['qId']
        d['qText'] = question['qText']
        if 'Resources' in res:
            d['Resources'] = res['Resources']
        else:
            d['Resources'] = []
        if question_counter < number_of_questions - 1:
            output.write(json.dumps(d, sort_keys=True) + ",\n")
        else:
            output.write(json.dumps(d, sort_keys=True) + "\n")
        question_counter += 1
    output.write(']')


def measure_performance(qlist, dblist):
    partial_match = 0
    exact_match = 0
    concepts_gs = 0
    concepts_gen_correct = 0
    concepts_gen_all = 0
    perq_precision = 0
    perq_recall = 0
    perq_f1 = 0
    total = len(qlist)
    for question, res in zip(qlist, dblist):
        found_one = False
        found_all = True
        n_correct = 0
        missed = set()
        extra = set([c['@surfaceForm'] for c in res['Resources']])

        for concept in question['Concept']:
            found_any = False
            concepts_gs += 1
            for resource in res['Resources']:
                res_name = resource['@URI'].rsplit('/', 1)[1]
                res_name = urllib.unquote(res_name)
                if res_name.replace("_", " ") == concept['fullLabel']:
                    n_correct += 1
                    found_one = True
                    found_any = True
                    try:
                        extra.remove(resource['@surfaceForm'])
                    except KeyError:
                        pass
            if found_any is False:
                found_all = False
                missed.add(concept['fullLabel'])
        if found_one is False:
            print("no match found for %s [%s] :: %s" % (str(question['qId']), question['qText'], question['Concept']))
            continue
        if found_all is True and len(question['Concept']) == len(res['Resources']):
            print("full match for %s, %d concepts" % (str(question['qId']), len(question['Concept'])))
            exact_match += 1
        else:
            print("partial_match for %s [%s] :: missed %s, extra %s" % (question['qId'], question['qText'], missed, extra))
            partial_match += 1

        concepts_gen_correct += n_correct
        concepts_gen_all += len(res['Resources'])

        precision = n_correct / float(len(res['Resources']))
        recall = n_correct / float(len(question['Concept']))
        perq_precision += precision
        perq_recall += recall
        perq_f1 += 2*(precision*recall)/(precision+recall)

    perq_precision = float(perq_precision) / total
    perq_recall = float(perq_recall) / total
    perq_f1 = float(perq_f1) / total

    print ""
    print("---")
    print(":: per-question statistics")
    print("exact match: {0} questions".format(exact_match))
    print("partial_match: {0} questions".format(partial_match))
    print("not found: {0} questions".format(total - (partial_match + exact_match)))
    print("partial or exact match: {0}% questions".format((exact_match + partial_match) / float(total) * 100))
    print("precision %.3f%%, recall %.3f%%, F1 %.3f%%" % (perq_precision * 100, perq_recall * 100, perq_f1 * 100))

    print ""
    print(":: per-entity statistics")
    precision = (concepts_gen_correct / float(concepts_gen_all))
    recall = (concepts_gen_correct / float(concepts_gs))
    print("precision: {0}/{1}, {2}% ".format
          (concepts_gen_correct, concepts_gen_all,
           precision * 100))
    print("recall: {0}/{1}, {2}% ".format
          (concepts_gen_correct, concepts_gs,
           recall * 100))
    print("F1 %.3f%%" % (2 * (precision * recall) / (precision + recall) * 100,))



def main():
    dataset = json.load(open(sys.argv[1], 'r'))
    #query_dump(dataset, "sys.argv[2]")
    res = json.load(open(sys.argv[2], 'r'))
    measure_performance(dataset, res)

if __name__ == '__main__':
    main()