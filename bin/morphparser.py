import sys
import getopt

import paradigmextract.morphparser as morphparser


def main(argv):

    options, remainder = getopt.gnu_getopt(argv[1:], 'tk:n:p:dr:c',
                                           ['tables', 'kbest', 'ngram', 'prior', 'debug', 'pprior', 'choose'])

    print_tables = False
    kbest = 1
    ngramorder = 3
    ngramprior = 0.01
    debug = False
    pprior = 1.0
    choose = False
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
        elif opt in ('-c', '--choose'):
            choose = True
    inp = iter(lambda: sys.stdin.readline().decode('utf-8'), '')
    paras, numexamples, lms, alphabet = morphparser.build(sys.argv[1], ngramorder, ngramprior)
    res = []
    for line in inp:
        res.append(morphparser.test_paradigms(line, paras, numexamples, lms, debug, pprior, choose))

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
