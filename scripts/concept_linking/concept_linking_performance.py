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
import csv
qid_rank_dict = {}


def calculate_mrr(qid_set, prop=0, exact_mrr=0):
    global qid_rank_dict
    rank_sum = 0
    count = float(len(qid_set))
    for qId in qid_set:
        rank = int(qid_rank_dict[qId]) + 1 # rank begins at -1
        if rank != 0:
            rank_sum += (1 / rank)
    mrr = rank_sum / count
    mrr_wd = (exact_mrr - mrr) * prop
    return mrr, mrr_wd


#loads a file with a json array and creates a corresponding dictionary with qIds as key
def load_from_tsv(filename):
    global qid_rank_dict
    file = open(filename)
    for line in csv.reader(file, delimiter='\t'):
        # dictionary[qId] = rank
        qid_rank_dict[line[0]] = line[4]
    return qid_rank_dict


def compare(dataset, correct):
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
    for entry, standard in zip(dataset, correct):
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
        else:
            print("partial_match for %s [%s] :: missed %s, extra %s" % (entry['qId'], entry['qText'], missed, extra))
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

    exact_prop = len(exact_match_set) / float(total)
    partial_more_prop = len(partial_more_set) / float(total)
    partial_missing_prop = len(partial_missing) / float(total)
    none_found_prop = len(none_found_set) / float(total)

    print()
    print("---")
    print(":: per-question statistics (macro measure)")
    print("exact match: %d questions (%.3f%%)" % (len(exact_match_set), exact_prop * 100))
    print("partial_match (extra): %d questions (%.3f%%)" % (len(partial_more_set), partial_more_prop * 100))
    print("partial_match (missing): %d questions (%.3f%%)" % (len(partial_missing), partial_missing_prop * 100))
    print("not found: %d questions (%.3f%%)" % (len(none_found_set), none_found_prop * 100))
    print("precision %.3f%%, recall %.3f%%, F1 %.3f%%" % (perq_precision * 100, perq_recall * 100, perq_f1 * 100))

    print()
    print(":: per-entity statistics (micro measure)")
    precision = (concepts_gen_correct / float(concepts_gen_all))
    recall = (concepts_gen_correct / float(concepts_gs))
    print("precision: %d/%d, %.3f%% " %
          (concepts_gen_correct, concepts_gen_all,
           precision * 100))
    print("recall: %d/%d, %.3f%% " %
          (concepts_gen_correct, concepts_gs,
           recall * 100))
    print("F1 %.3f%%" % (2 * (precision * recall) / (precision + recall) * 100,))

    print()
    print(":: answer MRR per entity error type (wΔ is MRR drop against correct weighted by question proportion)")
    exact_mrr = calculate_mrr(exact_match_set)[0]
    print("MRR for questions with exact match of concepts: %.3f" % exact_mrr)
    print("MRR for questions with superfluous concepts:    %.3f (wΔ %.3f)" % calculate_mrr(partial_more_set, partial_more_prop, exact_mrr))
    print("MRR for questions with missing concepts:        %.3f (wΔ %.3f)" % calculate_mrr(partial_missing, partial_missing_prop, exact_mrr))
    print("MRR for questions with no concepts at all:      %.3f (wΔ %.3f)" % calculate_mrr(none_found_set, none_found_prop, exact_mrr))
    print("total MRR: %.3f" % (calculate_mrr(total_mrr)[0]))


def main():
    dataset = json.load(open(sys.argv[1], 'r'))
    correct = json.load(open(sys.argv[2], 'r'))
    load_from_tsv(sys.argv[3])
    compare(dataset, correct)


if __name__ == '__main__':
    main()
