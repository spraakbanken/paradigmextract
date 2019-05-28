import functools
import itertools
import re
import paradigmextract.paradigm as paradigm
import time


def learnparadigms2(inflectiontables):
    vartables = []
    table_limit = 16
    count = 0
    for (identifier, (table, tagtable)) in inflectiontables:
        print('on: ', count)
        count += 1
        tablehead = table[0]
        taghead = tagtable[0]
        wg = [WordGraph.wordtograph(x) for x in table]
        result = functools.reduce(lambda x, y: x & y, wg)
        lcss = result.longestwords
        if not lcss:  # Table has no LCS - no variables
            vartables.append((identifier, tablehead, taghead, [[table, table, table, [], 0, 0]], tagtable))
            continue

        combos = []
        for lcs in lcss:
            factorlist = [_findfactors(w, lcs) for w in table]
            factorlist = _filterbracketings(factorlist, (_ffilter_lcp, _ffilter_shortest_string, _ffilter_shortest_infix,
                                                         _ffilter_longest_single_var, _ffilter_leftmost_sum), table_limit)
            combinations = itertools.product(*factorlist)
            for c in combinations:
                (numvars, variablelist) = _evalfact(lcs, c)
                infixcount = functools.reduce(lambda x, y: x + _count_infix_segments(y), c, 0)
                variabletable = [_string_to_varstring(s, variablelist) for s in c]
                combos.append([table, c, variabletable, variablelist, numvars, infixcount])

        vartables.append((identifier, tablehead, taghead, combos, tagtable))

    filteredtables = []

    for identifier, idform, idtag, t, tags in vartables:
        besttable = min(t, key=lambda s: (s[4], s[5]))
        filteredtables.append((identifier, idform, idtag, besttable, tags))

    print("collapse")
    before_t = time.time()
    identifier_to_paradigm, paradigmlist = _collapse_tables2(filteredtables)
    print("collapse done, took:", time.time() - before_t)

    return identifier_to_paradigm, paradigmlist


def learnparadigms(inflectiontables):
    vartables = []
    table_limit = 16
    count = 0
    for table, tagtable in inflectiontables:
        print('on: ', count)
        count += 1
        tablehead = table[0]
        taghead = tagtable[0]
        wg = [WordGraph.wordtograph(x) for x in table]
        result = functools.reduce(lambda x, y: x & y, wg)
        lcss = result.longestwords
        if not lcss:  # Table has no LCS - no variables
            vartables.append((tablehead, taghead, [[table, table, table, [], 0, 0]], tagtable))
            continue

        combos = []
        for lcs in lcss:
            factorlist = [_findfactors(w, lcs) for w in table]
            factorlist = _filterbracketings(factorlist, (_ffilter_lcp, _ffilter_shortest_string, _ffilter_shortest_infix,
                                                         _ffilter_longest_single_var, _ffilter_leftmost_sum), table_limit)
            combinations = itertools.product(*factorlist)
            for c in combinations:
                (numvars, variablelist) = _evalfact(lcs, c)
                infixcount = functools.reduce(lambda x, y: x + _count_infix_segments(y), c, 0)
                variabletable = [_string_to_varstring(s, variablelist) for s in c]
                combos.append([table, c, variabletable, variablelist, numvars, infixcount])

        vartables.append((tablehead, taghead, combos, tagtable))

    filteredtables = []

    for idform, idtag, t, tags in vartables:
        besttable = min(t, key=lambda s: (s[4], s[5]))
        filteredtables.append((idform, idtag, besttable, tags))

    print("collapse")
    before_t = time.time()
    paradigmlist = _collapse_tables(filteredtables)
    print("collapse done, took:", time.time() - before_t)

    return paradigmlist


class WordGraph:
    """
    Wordgraph class to extract LCS
    Convert word w to directed graph that contains all subsequences of w.
    """

    @classmethod
    def wordtograph(cls, word):
        trans = {}
        for i in range(len(word)):
            for j in range(i, len(word)):
                if (i, word[j]) not in trans:
                    trans[(i, word[j])] = j + 1
        grph = cls(trans)
        return grph

    """Simple directed graph class where graphs are special types of automata
       where each state is a final state.
       This is used to quickly find the LCS of a large number of words by
       first converting each word w to an automaton that accepts all substrings
       of w.  Then the automata can be intersected with __and__, and the
       longest path(s) extracted from the result with _maxpath().
    """

    def __init__(self, transitions):
        self.alphabet = {symbol for (state, symbol) in transitions}
        self.states = {state for (state, symbol) in transitions} | set(transitions.values())
        self.transitions = transitions
        self.revtrans = {}
        for (state, sym) in self.transitions:
            if self.transitions[(state, sym)] in self.revtrans:
                self.revtrans[self.transitions[(state, sym)]] |= {(state, sym)}
            else:
                self.revtrans[self.transitions[(state, sym)]] = {(state, sym)}

    def __getattr__(self, attr):
        if attr == 'longestwords':
            self._maxpath()
            return self.longestwords
        raise AttributeError("%r object has no attribute %r" % (self.__class__, attr))

    def __and__(self, other):
        return self._intersect(other)

    def _intersect(self, other):
        """Calculate intersection of two directed graphs."""
        alphabet = self.alphabet & other.alphabet
        stack = [(0, 0)]
        statemap = {(0, 0): 0}
        nextstate = 1
        trans = {}
        while len(stack) > 0:
            (asource, bsource) = stack.pop()
            for sym in alphabet:
                if (asource, sym) in self.transitions and (bsource, sym) in other.transitions:
                    atarget = self.transitions[(asource, sym)]
                    btarget = other.transitions[(bsource, sym)]
                    if (atarget, btarget) not in statemap:
                        statemap[(atarget, btarget)] = nextstate
                        nextstate += 1
                        stack.append((atarget, btarget))
                    trans[(statemap[(asource, bsource)], sym)] = statemap[(atarget, btarget)]

        return WordGraph(trans)

    def _backtrace(self, maxsources, maxlen, state, tempstring):
        if state not in self.revtrans:
            tempstring.reverse()
            self.longestwords.append("".join(tempstring))
            return
        for (backstate, symbol) in self.revtrans[state]:
            if maxlen[backstate] == maxlen[state] - 1:
                self._backtrace(maxsources, maxlen, backstate, tempstring + [symbol])

    def _maxpath(self):
        """Returns a list of strings that represent the set of longest words
           accepted by the automaton."""
        tr = {}
        # Create tr which simply has graph structure without symbols
        for (state, sym) in self.transitions:
            if state not in tr:
                tr[state] = set()
            tr[state].update({self.transitions[(state, sym)]})

        S = {0}
        maxlen = {}
        maxsources = {}
        for i in self.states:
            maxlen[i] = 0
            maxsources[i] = {}

        step = 1
        while len(S) > 0:
            Snew = set()
            for state in S:
                if state in tr:
                    for target in tr[state]:
                        if maxlen[target] < step:
                            maxsources[target] = {state}
                            maxlen[target] = step
                            Snew.update({target})
                        elif maxlen[target] == step:
                            maxsources[target] |= {state}
            S = Snew
            step += 1

        endstates = [key for key, val in maxlen.items() if val == max(maxlen.values())]
        self.longestwords = []
        for w in endstates:
            self._backtrace(maxsources, maxlen, w, [])


def _longest_variable(string):
    thislen = 0
    maxlen = 0
    inside = 0
    for s in string:
        if inside and s != u']':
            thislen += 1
        elif s == u']':
            inside = 0
            maxlen = max(thislen, maxlen)
        elif s == u'[':
            inside = 1
            thislen = 0
    return maxlen


def _count_infix_segments(string):
    """Counts total number of infix segments, ignores @-strings."""
    if u'[' not in string:
        return 0
    if u'@' in string:
        return 0
    nosuffix = re.sub('\][^\]]*$', ']', string)
    noprefix = re.sub('^[^\[]*\[', '[', nosuffix)
    nobrackets = re.sub('\[[^\]]*\]', '', noprefix)
    return len(nobrackets)


def _string_to_varstring(string, variables):
    varpos = 0
    s = []
    idx = 0
    while idx < len(string):
        if string[idx] == u'[':
            if idx != 0:
                s.append(u'+')
            idx += 1
            while string[idx] != u']':
                idx += len(variables[varpos])
                s.append(str(varpos + 1))
                if idx < len(string) - 1:
                    s.append(u'+')
                varpos += 1
            idx += 1
            continue
        else:
            s.append(string[idx])
            idx += 1

    return u''.join(s)


def _lcp(lst):
    """Returns the longest common prefix from a list."""
    if not lst:
        return ''
    cleanlst = list(map(lambda x: x.replace(u'[', '').replace(u']', ''), lst))
    s1 = min(cleanlst)
    s2 = max(cleanlst)
    for i, c in enumerate(s1):
        if c != s2[i]:
            return s1[:i]
    return s1


def _firstvarmatch(string, prefix) -> bool:
    """See if first var is exactly prefix."""
    return string[1:1 + len(prefix)] == prefix


def _evalfact(lcs, c):
    """Input: a list of variable-bracketed strings, the known LCS
       Output: number of variables needed and the variables themselves in a list."""
    allbreaks = []
    for w in c:
        breaks = [0] * len(lcs)
        p = 0
        inside = 0
        for pos in w:
            if pos == u'[':
                inside = 1
            elif pos == u']':
                inside = 0
                breaks[p - 1] = 1
            else:
                if inside:
                    p += 1

        allbreaks.append(breaks)
    finalbreaks = [0] * len(lcs)
    for br in allbreaks:
        for idx, val in enumerate(br):
            if val == 1:
                finalbreaks[idx] = 1

    # Extract vars
    variables = []
    currvar = u''
    for idx, val in enumerate(lcs):
        currvar += lcs[idx]
        if finalbreaks[idx] == 1:
            variables.append(currvar)
            currvar = u''

    numvars = sum(finalbreaks)
    return numvars, variables


def _findfactors(word, lcs):
    """Recursively finds the different ways to place an LCS in a string."""

    word = list(word)
    lcs = list(lcs)
    factors = []

    def rec(word, lcs, posw, posl, inmatch, tempstring):
        if posw == len(word) and posl != len(lcs):
            return
        if posw != len(word) and posl == len(lcs):
            if inmatch:
                rec(word, lcs, posw + 1, posl, 0, tempstring + [u']'] + [word[posw]])
            else:
                rec(word, lcs, posw + 1, posl, 0, tempstring + [word[posw]])
            return

        if posw == len(word) and posl == len(lcs):
            if inmatch:
                factors.append("".join(tempstring + [u']']))
            else:
                factors.append("".join(tempstring))
            return

        if word[posw] == lcs[posl]:
            if inmatch:
                rec(word, lcs, posw + 1, posl + 1, 1, tempstring + [word[posw]])
            else:
                rec(word, lcs, posw + 1, posl + 1, 1, tempstring + [u'['] + [word[posw]])

        if inmatch:
            rec(word, lcs, posw + 1, posl, 0, tempstring + [u']'] + [word[posw]])
        else:
            rec(word, lcs, posw + 1, posl, 0, tempstring + [word[posw]])

    rec(word, lcs, 0, 0, 0, [])
    return factors[:]


def _vars_to_string(baseform, varlist):
    vstr = [(str(idx + 1), v) for idx, v in enumerate(varlist)]
    return [("first-attest", baseform)] + vstr


def _collapse_tables2(tables):
    """Input: list of tables
       Output: Collapsed paradigms."""
    idx_to_paradigm = dict()
    identifier_to_paradigm = dict()
    collapsedidx = set()  # Store indices to collapsed tables
    for idx, (identifier, idform, idtag, besttable, tags) in enumerate(tables):
        t = besttable
        if idx in collapsedidx:
            identifier_to_paradigm[identifier] = idx_to_paradigm[idx]
            continue
        varstring = []
        vartable = t[2]
        # Find similar tables
        new_blabla = set()
        for idx2, (identifier2, idform2, idtag2, besttable2, tags2) in enumerate(tables):
            t2 = besttable2
            if idx2 != idx and vartable == t2[2] and tags == tags2:
                varstring.append(_vars_to_string(idform2, t2[3]))
                new_blabla.add(idx2)
        varstring.append(_vars_to_string(idform, t[3]))
        formlist = zip(t[2], tags)
        try:
            p = paradigm.Paradigm(formlist, varstring)
            idx_to_paradigm[idx] = p
            for bla in list(new_blabla):
                idx_to_paradigm[bla] = p
            identifier_to_paradigm[identifier] = p
            collapsedidx.update(new_blabla)
        except:
            print(formlist)
            print(varstring)
            raise
    return identifier_to_paradigm, list(idx_to_paradigm.values())


def _collapse_tables(tables):
    """Input: list of tables
       Output: Collapsed paradigms."""
    paradigms = []
    collapsedidx = set()  # Store indices to collapsed tables
    for idx, tab in enumerate(tables):
        tags = tab[3]
        t = tab[2]
        if idx in collapsedidx:
            continue
        varstring = []
        vartable = t[2]
        # Find similar tables
        for idx2, tab2 in enumerate(tables):
            t2 = tab2[2]
            if idx2 != idx and vartable == t2[2] and tags == tab2[3]:
                varstring.append(_vars_to_string(tab2[0], t2[3]))
                collapsedidx.update({idx2})
        varstring.append(_vars_to_string(tab[0], t[3]))
        formlist = zip(t[2], tags)
        try:
            p = paradigm.Paradigm(formlist, varstring)
        except:
            print(formlist)
            print(varstring)
            raise
        paradigms.append(p)
    return paradigms


def _ffilter_lcp(factorlist):
    flatten = lambda x: [y for l in x for y in flatten(l)] if type(x) is list else [x]
    lcprefix = _lcp(flatten(factorlist))
    factorlist = [[x for x in w if _firstvarmatch(x, lcprefix)] for w in factorlist]
    return factorlist


def _ffilter_shortest_string(factorlist):
    return [[x for x in w if len(x) == len(min(w, key=len))] for w in factorlist]


def _ffilter_shortest_infix(factorlist):
    return [
        [x for x in w if _count_infix_segments(x) == _count_infix_segments(min(w, key=lambda x: _count_infix_segments(x)))]
        for w in factorlist]


def _ffilter_longest_single_var(factorlist):
    return [[x for x in w if _longest_variable(x) == _longest_variable(max(w, key=lambda x: _longest_variable(x)))] for w
            in factorlist]


def _ffilter_leftmost_sum(factorlist):
    return [[x for x in w if sum(i for i in range(len(x)) if x.startswith('[', i)) == min(
        map(lambda x: sum(i for i in range(len(x)) if x.startswith('[', i)), w))] for w in factorlist]


def _filterbracketings(factorlist, functionlist, tablecap):
    def numcombinations(f):
        return functools.reduce(lambda x, y: x * len(y), f, 1)
    if numcombinations(factorlist) > tablecap:
        for filterfunc in functionlist:
            factorlist = filterfunc(factorlist)
            if numcombinations(factorlist) <= tablecap:
                break
    return factorlist
