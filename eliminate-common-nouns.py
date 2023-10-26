#!/usr/bin/env python3

import sys
import os.path

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
# Discards English words
#

with open ("wordsEn.txt", "r") as file:
    englishWords=file.read().split()

with open (filename, "r") as file:
    for line in file:
        candidate = line.strip()
        if candidate.lower() not in englishWords:
            print(candidate)
