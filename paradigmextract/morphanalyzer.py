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

import paradigmextract.genregex as genregex


def escape_fixed_string(string):
    """Fixed strings have _ to represent 0 (epsilon)."""
    if string == '_':
        return '0'
    else:
        return '{' + string + '}'


def nospace(string):
    return string.replace(' ','=').replace('_','=')


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
        # if paradigm.count < 3 and grammarname == 'Gunconstrained':
        #     continue
        par_is_constrained[paradigm.name] = False
        parstrings = []
        for formnumber, form in enumerate(paradigm.forms):
            tagstrings = map(lambda msd: '"' + msd[0] + '"' + ' = ' + '"' + msd[1] + '"' , form.msd)
            parstring = ''
            for idx, (is_var, slot) in enumerate(paradigm.slots):
                if is_var:
                    parvarname = nospace(paradigm.name) + '=var' + str(idx)
                    if parvarname not in parvars:
                        r = genregex.genregex(slot, pvalue = pval, length = False)
                        parvars[parvarname] = True
                        if r.fomaregex() != '?+':
                            par_is_constrained[paradigm.name] = True
                        defstring += 'def ' + parvarname + ' ' + r.fomaregex().replace('?', 'Alph') + ';\n'
                    parstring += ' [' + parvarname + '] '
                else:
                    thisslot = escape_fixed_string(slot[formnumber])
                    baseformslot = escape_fixed_string(slot[0])
                    parstring += ' [' + thisslot + ':' + baseformslot + '] '
            parstring += '0:["[" ' + ' " " '.join(tagstrings) + ' "]"]'
            parstrings.append(parstring)
        # if grammarname != 'Gcodnstrained' or par_is_constrained[paradigm.name]:
        rstring += 'def ' + nospace(paradigm.name) + '|\n'.join(parstrings) + ';\n'
    
    # parnames = [nospace(paradigm.name) for paradigm in paradigms if ' ' not in paradigm.name]
    parnames = []
    for paradigm in paradigms:
        # if ' ' not in paradigm.name and (grammarname != 'Gconstrdained' or par_is_constrained[paradigm.name]):
        parnames.append(nospace(paradigm.name))
    
    rstring += 'def ' + grammarname + ' ' + ' | '.join(parnames) + ';'
    
    return alphstring + defstring + rstring
