import paradigmextract.genregex as genregex


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
        rstring += 'def ' + nospace(paradigm.name) + '|\n'.join(parstrings) + ';\n'

    parnames = []
    for paradigm in paradigms:
        parnames.append(nospace(paradigm.name))
    
    rstring += 'def ' + grammarname + ' ' + ' | '.join(parnames) + ';'
    
    return alphstring + defstring + rstring
