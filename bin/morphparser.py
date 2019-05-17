# Do morphological analysis based on learned paradigms
# Reads one or more whitespace-separated words from STDIN and
# returns the most plausible analysis for the set in the format:
# SCORE  NAME_OF_PARADIGM  VARIABLES  WORDFORM1:BASEFORM,MSD#WORDFORM2:BASEFORM,MSD...

# Flags:
# -k num   print the k best analyses
# -t       print the entire table for the best analysis
# -d       print debug info
# -n num   use an nth order ngram model for selecting best paradigm
#          (an n-gram model for variables in the paradigm is used)

# Example:
# echo "coger cojo" | python morphparser.py ./../paradigms/spanish_verbs.p -k 1 -t
#
# Output:

# -11.231539838 coger (1=co) coger:coger,type=infinitive#cojo:coger,person=1st,number=singular,tense=present,mood=indicative
# *coger*	type=infinitive
# cogiendo	type=participle,tense=present
# cogido	type=participle,tense=past
# *cojo*	person=1st,number=singular,tense=present,mood=indicative
# coges	person=2nd,number=singular,tense=present,mood=indicative
# coge	person=3rd,number=singular,tense=present,mood=indicative
# ...
from typing import Tuple, List, Dict, Set
import sys
import getopt
import json

import paradigmextract.morphparser as morphparser
import paradigmextract.paradigm as paradigm


def build(inpfile: str, ngramorder: int, ngramprior: float, small: bool = False, lexicon: str = '',
          inpformat: str = 'pfile',
          pos: str = '') -> Tuple[List[paradigm.Paradigm], int, Dict[str, Tuple[float, List[morphparser.StringNgram]]], Set[str]]:
    if inpformat == 'pfile':
        paradigms = paradigm.load_p_file(inpfile, lex=lexicon)
    elif inpformat == 'jsonfile':
        paradigms = paradigm.load_json_file(inpfile, lex=lexicon, pos=pos)
    elif inpformat == 'json':
        paradigms = paradigm.load_json(json.loads(inpfile), lex=lexicon, pos=pos)
    else:
        raise RuntimeError('Wrong input format')

    # lexicon is removed from build in morphparser

    return morphparser.build(paradigms, ngramorder, ngramprior, small=small)


def main(argv):

    options, remainder = getopt.gnu_getopt(argv[1:], 'tk:n:p:dr:c',
                                           ['tables', 'kbest', 'ngram', 'prior', 'debug', 'pprior'])

    print_tables = False
    kbest = 1
    ngramorder = 3
    ngramprior = 0.01
    debug = False
    pprior = 1.0
    for opt, arg in options:
        if opt in ('-t', '--tables'):
            print_tables = True
        elif opt in ('-k', '--kbest'):
            kbest = int(arg)
        elif opt in ('-n', '--ngram'):
            ngramorder = int(arg)
        elif opt in ('-p', '--prior'):
            ngramprior = float(arg)
        elif opt in ('-d', '--debug'):
            debug = True
        elif opt in ('-d', '--debug'):
            debug = True
        elif opt in ('-r', '--pprior'):
            pprior = float(arg)
    inp = iter(lambda: sys.stdin.readline().decode('utf-8'), '')
    paras, numexamples, lms, alphabet = build(sys.argv[1], ngramorder, ngramprior)
    res = []
    for line in inp:
        res.append(morphparser.test_paradigms(line, paras, numexamples, lms, pprior))

    for words, analyses in res:
        # Print all analyses + optionally a table
        for aindex, (score, p, v) in enumerate(analyses):
            if aindex >= kbest:
                break
            varstring = '(' + ','.join([str(feat) + '=' + val for feat, val in zip(range(1, len(v)+1), v)]) + ')'
            table = p(*v)          # Instantiate table with vars from analysis
            baseform = table[0][0]
            matchtable = [(form, msd) for form, msd in table if form in words]
            wordformlist = [form + ':' + baseform + ',' + ','.join([m[0] + '=' + m[1] for m in msd]) for form, msd in matchtable]
            print((str(score) + ' ' + p.name + ' ' + varstring + ' ' + '#'.join(wordformlist)).encode("utf-8"))
            if print_tables:
                for form, msd in table:
                    if form in words:
                        form = "*" + form + "*"
                    msdprint = ','.join([m[0] + '=' + m[1] for m in msd])
                    print((form + '\t' + msdprint).encode("utf-8"))

            if debug:
                print("Members:", ", ".join([p(*[var[1] for var in vs])[0][0] for vs in p.var_insts]))
    print()


if __name__ == "__main__":
    main(sys.argv)
