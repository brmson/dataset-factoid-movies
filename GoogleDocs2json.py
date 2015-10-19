import sys

# This script parses the tsv from our google doc to a json format
# It creates both train and test datasets by juggling the output writer reference

# save the json output as output.json 

argv = sys.argv
input_filename = argv[1]
output_filename = argv[2]
train = file(output_filename + "-train.json", 'w')
test = file(output_filename + "-test.json", 'w')

train.write('[\n')
test.write('[\n')
jsfile = train
with open(input_filename,'r') as f:
    reader=f.readlines()
    i = 1
    last_train = len(reader)
    last_test = 0
    while (last_test + 4) < last_train:
        last_test += 4
    for line in reader:
        if (i%4 == 0):
            jsfile = test
        else:
            jsfile = train
        words = line.split("\t")[1:]
        jsfile.write('{')
        jsfile.write('"qId\": \"mfb' + str(i).zfill(6) + '\", ')
        jsfile.write('"qText\": \"' + words[1] + '\", ')
        jsfile.write("\"answers\": [")
        jsfile.write("\""+words[2]+"\"")
        j = 3
        
        while (words[j] != "" and j<len(words)-1): #iterate through answers
            jsfile.write(", \""+words[j]+"\"")
            j+=1
        jsfile.write("], ")
        jsfile.write("\"author\": "+"\""+words[0]+"\"")
        jsfile.write('}')
       
        if (i == last_test or i == last_train):
            jsfile.write('\n')
            i += 1
            continue
        jsfile.write(',')
        jsfile.write('\n')
        i += 1
    train.write(']')
    test.write(']')
    print("processed "+str(last_train)+" entries")
train.close()
test.close()
