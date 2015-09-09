#!/usr/bin/pypy
# Measures YodaQA concept linking performance
# requires the fixed QuestionDump json and the dataset
# exact match means all correct concepts were found
# partial match means -some- (atleast one) correct concept were found
# incorrect means no expected concept was found
# then there is the total number of concepts found vs expected
# ...as precision (correct_found / all_found) and recall (correct_found / correct_all)
# usage:
# python concept_linking_performance.py questionDump.json correct_dataset.json
from __future__ import print_function
import sys
import json
import itertools


def compare(dataset, correct):
    partial_match = 0
    exact_match = 0
    concepts_gs = 0
    concepts_gen_correct = 0
    concepts_gen_all = 0
    perq_precision = 0
    perq_recall = 0
    perq_f1 = 0
    total = len(dataset)
    for entry, standard in itertools.izip(dataset, correct):
        if entry['qId'] != standard['qId']:
            print("Incorrect match. Please sort dataset")
            break
        found_one = False
        found_all = True
        n_correct = 0
        for concept in standard['Concept']:
            found_any = False
            concepts_gs += 1
            for concept2 in entry['Concept']:
                if concept['pageID'] == concept2['pageID']:
                    n_correct += 1
                    found_one = True
                    found_any = True
            if found_any is False:
                found_all = False
        if found_one is False:
            print("no match found for " + str(entry['qId']))
            continue
        if found_all is True:
            print("full match for " + str(entry['qId']))
            exact_match += 1
        else:
            print("partial_match for " + str(entry['qId']))
            partial_match += 1

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
    print(":: per-answer statistics")
    precision = (concepts_gen_correct / float(concepts_gen_all))
    recall = (concepts_gen_correct / float(concepts_gs))
    print("precision: {0}/{1}, {2}% ".format
          (concepts_gen_correct, concepts_gen_all,
           precision * 100))
    print("recall: {0}/{1}, {2}% ".format
          (concepts_gen_correct, concepts_gs,
           recall * 100))
    print("F1 %.3f%%" % (2*(precision*recall)/(precision+recall) * 100,))


def main():
    dataset = json.load(open(sys.argv[1], 'r'))
    correct = json.load(open(sys.argv[2], 'r'))
    compare(dataset, correct)


if __name__ == '__main__':
    main()
