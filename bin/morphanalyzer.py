import getopt
import sys

import paradigmextract.morphanalyzer as morphanalyzer
import paradigmextract.paradigm as paradigm
import paradigmextract.genregex as genregex

### Create a foma-compatible morphological analyzer from paradigm file ###

# Options:
# -o  recreate original data (all vars must be exactly instantiated as seen in training data)
# -c  constrain variables by generalizing (default pvalue = 0.05)
# -u  unconstrained (all variables are defined as ?+)
# -p  <pvalue>  use <pvalue> together with -c
# -s  keep different analyzers separate instead of merging with priority union
#     (may be necessary for some analyzers)
# -n  name of binary foma file to compile to

# Any combination of the above may be used. The analyzers are combined by
# priority union, e.g. -o -c -u would yield an analyzer
# [ Goriginal .P. Gconstrained .P. Gunconstrained ]

# Example usage:
# python morphanalyzer.py -o -c ./../paradigms/spanish_verbs.p > spanish_verbs.foma


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


def escape_fixed_string(string):
    """Fixed strings have _ to represent 0 (epsilon)."""
    if string == '_':
        return '0'
    else:
        return '{' + string + '}'


def nospace(string):
    return string.replace(' ', '=').replace('_', '=')


def paradigms_to_alphabet(paradigms):
    """Extracts all used symbols from an iterable of paradigms."""
    alphabet = set()
    for paradigm in paradigms:
        for idx, (is_var, slot) in enumerate(paradigm.slots):
            for word in slot:
                alphabet |= set(word)
    return alphabet


def paradigms_to_foma(paradigms, grammarname, pval):
    """Converts iterable of paradigms to foma-script (as a string)."""
    parvars = {}
    rstring = ''
    defstring = ''
    par_is_constrained = {}

    alphabet = paradigms_to_alphabet(paradigms)
    alphabet = {'"' + a + '"' for a in alphabet}
    alphstring = 'def Alph ' + '|'.join(alphabet) + ';\n'

    for paradigm in paradigms:
        par_is_constrained[paradigm.name] = False
        parstrings = []
        for formnumber, form in enumerate(paradigm.forms):
            tagstrings = map(lambda msd: '"' + msd[0] + '"' + ' = ' + '"' + msd[1] + '"', form.msd)
            parstring = ''
            for idx, (is_var, slot) in enumerate(paradigm.slots):
                if is_var:
                    parvarname = nospace(paradigm.name) + '=var' + str(idx)
                    if parvarname not in parvars:
                        r = genregex.Genregex(slot, pvalue=pval, length=False)
                        parvars[parvarname] = True
                        if fomaregex(r) != '?+':
                            par_is_constrained[paradigm.name] = True
                        defstring += 'def ' + parvarname + ' ' + fomaregex(r).replace('?', 'Alph') + ';\n'
                    parstring += ' [' + parvarname + '] '
                else:
                    thisslot = escape_fixed_string(slot[formnumber])
                    baseformslot = escape_fixed_string(slot[0])
                    parstring += ' [' + thisslot + ':' + baseformslot + '] '
            parstring += '0:["[" ' + ' " " '.join(tagstrings) + ' "]"]'
            parstrings.append(parstring)
        rstring += 'def ' + nospace(paradigm.name) + '|\n'.join(parstrings) + ';\n'

    parnames = []
    for paradigm in paradigms:
        parnames.append(nospace(paradigm.name))

    rstring += 'def ' + grammarname + ' ' + ' | '.join(parnames) + ';'

    return alphstring + defstring + rstring


def fomaregex(regex: genregex.Genregex):
    """
    A regex can be returned either for python or foma. The regex
    may need to check both the prefix and suffixes separately, which
    is easily done in a foma-style regex since we can intersect the
    prefix and suffix languages separately:

     [?* suffixes] & [prefixes ?*] & [?^{minlen, maxlen}]

    However, this can't be directly done in Python.  To simulate this,
    we check the suffix (and possible length constraints) by a lookahead
    which doesn't consume any symbols, before the checking the prefix, ie.

    ^(?=.*suffixes$)(?=.{minlen, maxlen})prefixes
    >>>print fomaregex(regex)
    [?* [{a}|{b}]] & [?^{1,2}] & [[{a}|{b}] ?*]
    :param regex:
    :return:
    """
    # [?* suffix] & [prefix ?*] & [?^{min,max}]
    def explode(string: str):
        return '{' + string + '}'

    re = []
    if len(regex.stringset) > 0:
        return '[' + u'|'.join(map(explode, regex.stringset)) + ']'
    if len(regex.suffixset) > 0:
        re.append('[?* [' + '|'.join(map(explode, regex.suffixset)) + ']]')
    if len(regex.lenrange) > 0:
        re.append('[?^{' + str(regex.lenrange[0]) + ',' + str(regex.lenrange[1]) + '}]')
    if len(regex.prefixset) > 0:
        re.append('[[' + '|'.join(map(explode, regex.prefixset)) + '] ?*]')
    if len(re) == 0:
        return u'?+'
    else:
        return ' & '.join(re)


if __name__ == "__main__":
    main(sys.argv)
