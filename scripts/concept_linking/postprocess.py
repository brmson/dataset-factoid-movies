#!/usr/bin/pypy
# postprocessing script. Typically you run the main function to process a fresh dataset from concept linking.
# However, you can run each part separatedly (for example, after a small fix in a already valid json)
# fix_json creates a valid JSON file
# usage: python postprocess.py dataset_from_webapi.json train.json output.json
from __future__ import print_function
import sys
import json


def fix_json(input_filename, output_filename):
    """
    Takes the output from webapi and creates a valid json array
    """
    json_to_fix = open(input_filename, 'r')
    fixed_json = open(output_filename, 'w')
    lines = json_to_fix.readlines()
    i = 0
    number_of_questions = len(lines)
    print("[", file=fixed_json)
    for line in lines:
        if (i == number_of_questions - 1):
            print (line.replace(",\n", ""), file = fixed_json)
        else:
            print (line.replace("\n", ""), file = fixed_json)
        i += 1
    print("]", file = fixed_json)

def find_duplicates(concept_list):
    """
    takes a json array and and returns a list of duplicates
    has O(n^2) complexity
    """
    enumerated_concept_list = enumerate(concept_list)
    duplicated_concepts = []
    for i, concept in enumerated_concept_list:
        for j in range(0, len(concept_list)):
            if (concept['qId'] == concept_list[j]['qId'] and i != j):
                if not concept['qId'] in duplicated_concepts:
                    print("duplicate found!")
                    print("first concept: " +str(i) +" " + str(concept['Concept']))
                    print("second concept " +str(j) + " " + str(concept_list[j]['Concept']))
                    duplicated_concepts.append(concept['qId'])
    return duplicated_concepts

def check_all_qIds(entity_linking_dataset, original_dataset):
    """
    takes a valid json and the original dataset return a list of missing questions
    """
    result_list = []
    for question in original_dataset:
        found = False
        for concept in entity_linking_dataset:
            if concept['qId'] == question['qId']:
                found = True
                break
        if found == False:
            result_list.append(question['qId'])
    return result_list

def sort(output_filename):
    """
    takes a filename of a valid json array and sorts it
    first by the origin and then the number 
    outputs it in the same file 
    """
    d = json.load(open(output_filename))
    d.sort(key=get_qId_last)
    d.sort(key=get_qId_first, reverse=True)
    output = open(output_filename,"w")
    i = 0
    number_of_questions = len(d)
    print("[", file=output)
    for entry in d:
        if (i != number_of_questions - 1):
            print('  %s,' % (json.dumps(entry, sort_keys=True),), file=output)
        else:
            print('  %s' % (json.dumps(entry, sort_keys=True),), file=output)
        i += 1
    print("]", file = output)
        

def get_qId_first(json):
    return json['qId'][:3]

def get_qId_last(json):
    return json['qId'][-6:]

def main():
    dataset_from_webapi = sys.argv[1]
    original_dataset = json.load(open(sys.argv[2], 'r'))
    output_filename = sys.argv[3]
    fix_json(dataset_from_webapi, output_filename)
    fixed_json = json.load(open(output_filename, 'r'))
    sort(output_filename)
    res = find_duplicates(fixed_json)
    if len(res) == 0:
        print("no duplicates")
    else:
        print("duplicates:")
        print(res)
    res = check_all_qIds(fixed_json, original_dataset)
    if len(res) == 0:
        print("all " + str(len(original_dataset)) + " questions are contained")
    else:
        print("missing:")
        print(str(res))
    print(str(len(fixed_json)) + "/" + str(len(original_dataset)) + "concepts")
if __name__ == "__main__": main()