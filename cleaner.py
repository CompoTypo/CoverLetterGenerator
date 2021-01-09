import sys
import io
import re

if len(sys.argv) is not 3:
    print("ERR Format: python cleaner.py <path/infile> <path/outfile>")

# Clean dataset
in_set = open(sys.argv[1])
out_set = open(sys.argv[2])

for line in in_set:
    words = line.split(', ')
    words[-1] = words[-1].strip('\n')
    words[-1] = words[-1].replace('.','')

    for word in words:
        try:
            int(word[0])
            out_set.write(word + ',')
        except:
            if word == '?':
                out_set.write('NA,')
            else:
                out_set.write('\"' + word + '\",')
    out_set.write('\n')


