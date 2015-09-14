#!/usr/bin/pypy
# Measures YodaQA concept linking performance
# requires the fixed QuestionDump json, the gold standard tsv file and the dataset
# exact match means all correct concepts were found
# partial match means -some- (atleast one) correct concept were found
# incorrect means no expected concept was found
# then there is the total number of concepts found vs expected
# ...as precision (correct_found / all_found) and recall (correct_found / correct_all)
# usage:
# python concept_linking_performance.py questionDump.json correct_dataset.json GS_dump.tsv
from __future__ import print_function
from __future__ import division
import sys
import json
import itertools
import csv
qid_rank_dict = {}


def calculate_mrr(qid_set):
    global qid_rank_dict
    rank_sum = 0
    count = float(len(qid_set))
    for qId in qid_set:
        rank = int(qid_rank_dict[qId]) + 1 # rank begins at -1
        if rank != 0:
            rank_sum += (1 / rank)
    mrr = rank_sum / count
    return mrr


#loads a file with a json array and creates a corresponding dictionary with qIds as key
def load_from_tsv(filename):
    global qid_rank_dict
    file = open(filename)
    for line in csv.reader(file, delimiter='\t'):
        # dictionary[qId] = rank
        qid_rank_dict[line[0]] = line[4]
    return qid_rank_dict


def compare(dataset, correct):
    partial_match = 0
    exact_match = 0
    concepts_gs = 0
    concepts_gen_correct = 0
    concepts_gen_all = 0
    perq_precision = 0
    perq_recall = 0
    perq_f1 = 0
    partial_more_set = set()
    partial_missing = set()
    exact_match_set = set()
    none_found_set = set()
    total_mrr = set()
    total = len(dataset)
    for entry, standard in itertools.izip(dataset, correct):
        total_mrr.add(entry['qId'])
        if entry['qId'] != standard['qId']:
            print("Incorrect match. Please sort dataset")
            break
        found_one = False
        found_all = True
        n_correct = 0
        missed = set()
        extra = set([c['fullLabel'] for c in entry['Concept']])
        for concept in standard['Concept']:
            found_any = False
            concepts_gs += 1
            for concept2 in entry['Concept']:
                if concept['pageID'] == concept2['pageID']:
                    n_correct += 1
                    found_one = True
                    found_any = True
                    try:
                        extra.remove(concept2['fullLabel'])
                    except KeyError:
                        pass
            if found_any is False:
                found_all = False
                missed.add(concept['fullLabel'])
        if found_one is False:
            print("no match found for %s [%s] :: %s" % (str(entry['qId']), entry['qText'], standard['Concept']))
            none_found_set.add(entry['qId'])
            continue
        if found_all is True and len(entry['Concept']) == len(standard['Concept']):
            print("full match for %s, %d concepts" % (str(entry['qId']), len(standard['Concept'])))
            exact_match_set.add(entry['qId'])
            exact_match += 1
        else:
            print("partial_match for %s [%s] :: missed %s, extra %s" % (entry['qId'], entry['qText'], missed, extra))
            partial_match += 1
            if len(extra) > 0 and len(missed) == 0:
                partial_more_set.add(entry['qId'])
            elif len(missed) > 0:
                partial_missing.add(entry['qId'])
            else:
                print(str(len(missed)) + " missing and " + str(len(extra)) + " extra")

        concepts_gen_correct += n_correct
        concepts_gen_all += len(entry['Concept'])

        precision = n_correct / float(len(entry['Concept']))
        recall = n_correct / float(len(standard['Concept']))
        perq_precision += precision
        perq_recall += recall
        perq_f1 += 2*(precision*recall)/(precision+recall)

    perq_precision = float(perq_precision) / total
    perq_recall = float(perq_recall) / total
    perq_f1 = float(perq_f1) / total

    print()
    print("---")
    print(":: per-question statistics")
    print("exact match: {0} questions".format(exact_match))
    print("partial_match: {0} questions".format(partial_match))
    print("not found: {0} questions".format(total - (partial_match + exact_match)))
    print("partial or exact match: {0}% questions".format((exact_match + partial_match) / float(total) * 100))
    print("precision %.3f%%, recall %.3f%%, F1 %.3f%%" % (perq_precision * 100, perq_recall * 100, perq_f1 * 100))

    print()
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

    print()
    print(":: statistics per error type")
    print("MRR for questions with exact match of concepts: {0}".format(calculate_mrr(exact_match_set)))
    print("MRR for questions with superfluous concepts:    {0}".format(calculate_mrr(partial_more_set)))
    print("MRR for questions with missing concepts:        {0}".format(calculate_mrr(partial_missing)))
    print("MRR for questions with no concepts at all:      {0}".format(calculate_mrr(none_found_set)))
    print("total MRR: " + str(calculate_mrr(total_mrr)))


def main():
    dataset = json.load(open(sys.argv[1], 'r'))
    correct = json.load(open(sys.argv[2], 'r'))
    load_from_tsv(sys.argv[3])
    compare(dataset, correct)


if __name__ == '__main__':
    main()
