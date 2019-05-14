import getopt
import sys

import paradigmextract.morphanalyzer as morphanalyzer
import paradigmextract.paradigm as paradigm


def main(argv):
    options, remainder = getopt.gnu_getopt(argv[1:],
                                           'ocup:sn:',
                                           ['original', 'constrained', 'unconstrained', 'pvalue', 'separate', 'name'])

    pv = 0.05

    (Goriginal, Gconstrained, Gunconstrained, Gseparate, Gname) = False, False, False, False, 'analyzer.bin'
    for opt, arg in options:
        if opt in ('-o', '--original'):
            Goriginal = True
        elif opt in ('-c', '--constrained'):
            Gconstrained = True
        elif opt in ('-u', '--unconstrained'):
            Gunconstrained = True
        elif opt in ('-s', '--separate'):
            Gseparate = True
        elif opt in ('-p', '--pvalue'):
            pv = float(arg)
        elif opt in ('-n', '--name'):
            Gname = arg

    paradigms = paradigm.load_p_file(remainder[0])

    analyzers = []
    analyzernames = []
    for analyzertype in (('Goriginal', 1.0), ('Gconstrained', pv), ('Gunconstrained', 0.0)):
        if eval(analyzertype[0]) == True:
            analyzers.append(morphanalyzer.paradigms_to_foma(paradigms, analyzertype[0], analyzertype[1]))
            analyzernames.append(analyzertype[0])

    for a in analyzers:
        print(a.encode('utf-8'))

    if len(analyzers) > 0:
        if Gseparate:
            for a in analyzernames:
                print('regex ' + a + ';')
        else:
            print('regex ' + u' .P. '.join(analyzernames) + ';')
        print('save stack ' + Gname)


if __name__ == "__main__":
    main(sys.argv)
