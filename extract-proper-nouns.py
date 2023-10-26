#!/usr/bin/env python3

import sys
import os.path

import nltk
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordTokenizer

#
# Parses arguments
#

if len(sys.argv) != 2:
    print('Usage:', sys.argv[0], '<text file>')
    sys.exit(1)

filename = sys.argv[1]

if not os.path.exists(filename):
    print(filename + ': no such file')
    sys.exit(2)

#
# Extract proper nouns
#

with open (filename, "r") as file:
    text=file.read().replace('\n', ' ').strip()

# First, the punkt tokenizer divides our text in sentences.
# Each sentence is then tokenized and POS tagged.
#
# Proper nouns receive the tags 'NPP', we discard first words of sentence to
# reduce the false positive rate. For example, in the following sentence,
# onomatopoeias are tagged as NPP: "Bang! Ssssssss! It exploded.".

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
for sentence in sent_detector.tokenize(text):
    tokenizedSentence = word_tokenize(sentence)
    taggedSentence = pos_tag(tokenizedSentence)
    start = True
    currentCandidate = []

    for word, pos in taggedSentence:
        if start:
            start = False
            continue

        if pos == 'NNP':
            currentCandidate.append(word)
            continue

        if len(currentCandidate) > 0:
            print(' '.join(currentCandidate))
            currentCandidate = []

    if len(currentCandidate) > 0:
        print(' '.join(currentCandidate))
