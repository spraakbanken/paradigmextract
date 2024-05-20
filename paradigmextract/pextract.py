"""Pextract."""

import functools
import itertools
import operator
import re

from paradigmextract import paradigm


def learnparadigms(inflectiontables: list[tuple[list[str], list[list[tuple[str, str]]]]]):  # noqa: ANN201, D103
    vartables = []
    table_limit = 16
    for table, tagtable in inflectiontables:
        tablehead = table[0]
        taghead = tagtable[0]
        wg = [WordGraph.from_string(x) for x in table]
        result = functools.reduce(operator.and_, wg)
        lcss = result.longestwords
        if not lcss:  # Table has no LCS - no variables
            vartables.append((tablehead, taghead, [[table, table, table, [], 0, 0]], tagtable))
            continue

        combos = []
        for lcs in lcss:
            factorlist = [_findfactors(w, lcs) for w in table]
            factorlist = _filterbracketings(
                factorlist,
                (
                    _ffilter_lcp,
                    _ffilter_shortest_string,
                    _ffilter_shortest_infix,
                    _ffilter_longest_single_var,
                    _ffilter_leftmost_sum,
                ),
                table_limit,
            )
            combinations = itertools.product(*factorlist)
            for c in combinations:
                (numvars, variablelist) = _evalfact(lcs, c)
                infixcount = functools.reduce(lambda x, y: x + _count_infix_segments(y), c, 0)
                variabletable = [_string_to_varstring(s, variablelist) for s in c]
                combos.append([table, c, variabletable, variablelist, numvars, infixcount])

        vartables.append((tablehead, taghead, combos, tagtable))

    filteredtables = []

    for idform, idtag, t, tags in vartables:
        besttable = min(t, key=operator.itemgetter(4, 5))
        filteredtables.append((idform, idtag, besttable, tags))

    return _collapse_tables(filteredtables)


class WordGraph:
    """Wordgraph class to extract LCS.

    Convert word w to directed graph that contains all subsequences of w.

    Simple directed graph class where graphs are special types of automata
       where each state is a final state.
       This is used to quickly find the LCS of a large number of words by
       first converting each word w to an automaton that accepts all substrings
       of w.  Then the automata can be intersected with __and__, and the
       longest path(s) extracted from the result with _maxpath().
    """

    @classmethod
    def from_string(cls, word: str):  # noqa: ANN206, D102
        trans = {}
        for i in range(len(word)):
            for j in range(i, len(word)):
                if (i, word[j]) not in trans:
                    trans[(i, word[j])] = j + 1
        return cls(trans)

    def __init__(self, transitions) -> None:  # noqa: D107, ANN001
        self.alphabet = {symbol for (state, symbol) in transitions}
        self.states = {state for (state, symbol) in transitions} | set(transitions.values())
        self.transitions = transitions
        self.revtrans = {}
        for state, sym in self.transitions:
            if self.transitions[(state, sym)] in self.revtrans:
                self.revtrans[self.transitions[(state, sym)]] |= {(state, sym)}
            else:
                self.revtrans[self.transitions[(state, sym)]] = {(state, sym)}

    def __getattr__(self, attr):  # noqa: D105, ANN204, ANN001
        if attr == "longestwords":
            self._maxpath()
            return self.longestwords
        raise AttributeError(f"{self.__class__!r} object has no attribute {attr!r}")

    def __and__(self, other):  # noqa: D105, ANN204, ANN001
        return self._intersect(other)

    def _intersect(self, other):  # noqa: ANN202, ANN001
        """Calculate intersection of two directed graphs."""
        alphabet = self.alphabet & other.alphabet
        stack = [(0, 0)]
        statemap = {(0, 0): 0}
        nextstate = 1
        trans = {}
        while stack:
            (asource, bsource) = stack.pop()
            for sym in alphabet:
                if (asource, sym) in self.transitions and (
                    bsource,
                    sym,
                ) in other.transitions:
                    atarget = self.transitions[(asource, sym)]
                    btarget = other.transitions[(bsource, sym)]
                    if (atarget, btarget) not in statemap:
                        statemap[(atarget, btarget)] = nextstate
                        nextstate += 1
                        stack.append((atarget, btarget))
                    trans[(statemap[(asource, bsource)], sym)] = statemap[(atarget, btarget)]

        return WordGraph(trans)

    def _backtrace(self, maxsources, maxlen, state, tempstring) -> None:  # noqa: ANN001
        if state not in self.revtrans:
            tempstring.reverse()
            self.longestwords.append("".join(tempstring))
            return
        for backstate, symbol in self.revtrans[state]:
            if maxlen[backstate] == maxlen[state] - 1:
                self._backtrace(maxsources, maxlen, backstate, [*tempstring, symbol])

    def _maxpath(self) -> None:
        """Return a list of strings that represent the set of longest words accepted by the automaton."""  # noqa: E501
        tr = {}
        # Create tr which simply has graph structure without symbols
        for state, sym in self.transitions:
            if state not in tr:
                tr[state] = set()
            tr[state].update({self.transitions[(state, sym)]})

        S = {0}  # noqa: N806
        maxlen = {}
        maxsources = {}
        for i in self.states:
            maxlen[i] = 0
            maxsources[i] = {}

        step = 1
        while S:
            Snew = set()  # noqa: N806
            for state in S:
                if state in tr:
                    for target in tr[state]:
                        if maxlen[target] < step:
                            maxsources[target] = {state}
                            maxlen[target] = step
                            Snew.update({target})
                        elif maxlen[target] == step:
                            maxsources[target] |= {state}
            S = Snew  # noqa: N806
            step += 1

        endstates = [key for key, val in maxlen.items() if val == max(maxlen.values())]
        self.longestwords = []
        for w in endstates:
            self._backtrace(maxsources, maxlen, w, [])


def _longest_variable(string: str) -> int:
    """Compute the longest variable in the input.

    >>> _longest_variable("test[a]")
    1

    Args:
        string (str): the string to analyze

    Returns:
        int: the length of the longest variable
    """
    thislen = 0
    maxlen = 0
    inside = False
    for s in string:
        if inside and s != "]":
            thislen += 1
        elif s == "]":
            inside = False
            maxlen = max(thislen, maxlen)
        elif s == "[":
            inside = True
            thislen = 0
    return maxlen


def _count_infix_segments(string: str) -> int:
    """Count total number of infix segments, ignores @-strings."""
    if "[" not in string:
        return 0
    if "@" in string:
        return 0
    nosuffix = re.sub(r"\][^\]]*$", "]", string)
    noprefix = re.sub(r"^[^\[]*\[", "[", nosuffix)
    nobrackets = re.sub(r"\[[^\]]*\]", "", noprefix)
    return len(nobrackets)


def _string_to_varstring(string, variables):  # noqa: ANN202, ANN001
    varpos = 0
    s = []
    idx = 0
    while idx < len(string):
        if string[idx] == "[":
            if idx != 0:
                s.append("+")
            idx += 1
            while string[idx] != "]":
                idx += len(variables[varpos])
                s.append(str(varpos + 1))
                if idx < len(string) - 1:
                    s.append("+")
                varpos += 1
        else:
            s.append(string[idx])
        idx += 1
    return "".join(s)


def _lcp(lst):  # noqa: ANN202, ANN001
    """Return the longest common prefix from a list."""
    if not lst:
        return ""
    cleanlst = [x.replace("[", "").replace("]", "") for x in lst]
    s1 = min(cleanlst)
    s2 = max(cleanlst)
    return next((s1[:i] for i, c in enumerate(s1) if c != s2[i]), s1)


def _firstvarmatch(string, prefix) -> bool:  # noqa: ANN001
    """See if first var is exactly prefix."""
    return string[1 : 1 + len(prefix)] == prefix


def _evalfact(lcs, c):  # noqa: ANN001, ANN202
    """evalfact.

    Input: a list of variable-bracketed strings, the known LCS
    Output: number of variables needed and the variables themselves in a list.
    """
    allbreaks = []
    for w in c:
        breaks = [0] * len(lcs)
        p = 0
        inside = 0
        for pos in w:
            if pos == "[":
                inside = 1
            elif pos == "]":
                inside = 0
                breaks[p - 1] = 1
            elif inside:
                p += 1

        allbreaks.append(breaks)
    finalbreaks = [0] * len(lcs)
    for br in allbreaks:
        for idx, val in enumerate(br):
            if val == 1:
                finalbreaks[idx] = 1

    # Extract vars
    variables = []
    currvar = ""
    for idx, val in enumerate(lcs):
        currvar += val
        if finalbreaks[idx] == 1:
            variables.append(currvar)
            currvar = ""

    numvars = sum(finalbreaks)
    return numvars, variables


def _findfactors(word, lcs):  # noqa: ANN202, ANN001
    """Recursively finds the different ways to place an LCS in a string."""
    word = list(word)
    lcs = list(lcs)
    factors = []

    def rec(word, lcs, posw, posl, inmatch, tempstring) -> None:  # noqa: ANN001
        if posw == len(word) and posl != len(lcs):
            return
        if posw != len(word) and posl == len(lcs):
            if inmatch:
                rec(word, lcs, posw + 1, posl, 0, [*tempstring, "]", word[posw]])
            else:
                rec(word, lcs, posw + 1, posl, 0, [*tempstring, word[posw]])
            return

        if posw == len(word) and posl == len(lcs):
            if inmatch:
                factors.append("".join([*tempstring, "]"]))
            else:
                factors.append("".join(tempstring))
            return

        if word[posw] == lcs[posl]:
            if inmatch:
                rec(word, lcs, posw + 1, posl + 1, 1, [*tempstring, word[posw]])
            else:
                rec(word, lcs, posw + 1, posl + 1, 1, [*tempstring, "[", word[posw]])

        if inmatch:
            rec(word, lcs, posw + 1, posl, 0, [*tempstring, "]", word[posw]])
        else:
            rec(word, lcs, posw + 1, posl, 0, [*tempstring, word[posw]])

    rec(word, lcs, 0, 0, 0, [])
    return factors.copy()


def _vars_to_string(baseform, varlist):  # noqa: ANN202, ANN001
    vstr = [(str(idx + 1), v) for idx, v in enumerate(varlist)]
    return [("first-attest", baseform), *vstr]


def _collapse_tables(tables):  # noqa: ANN202, ANN001
    """Collapse tables.

    Input: list of tables
    Output: Collapsed paradigms.
    """
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
            print(formlist)  # noqa: T201
            print(varstring)  # noqa: T201
            raise
        paradigms.append(p)
    return paradigms


def _ffilter_lcp(factorlist):  # noqa: ANN202, ANN001
    def flatten(x):  # noqa: ANN202, ANN001
        return [y for l in x for y in flatten(l)] if isinstance(x, list) else [x]  # noqa: E741

    lcprefix = _lcp(flatten(factorlist))
    return [[x for x in w if _firstvarmatch(x, lcprefix)] for w in factorlist]


def _ffilter_shortest_string(factorlist):  # noqa: ANN202, ANN001
    return [[x for x in w if len(x) == len(min(w, key=len))] for w in factorlist]


def _ffilter_shortest_infix(factorlist):  # noqa: ANN202, ANN001
    return [
        [
            x
            for x in w
            if _count_infix_segments(x)
            == _count_infix_segments(min(w, key=_count_infix_segments))
        ]
        for w in factorlist
    ]


def _ffilter_longest_single_var(factorlist):  # noqa: ANN202, ANN001
    return [
        [
            x
            for x in w
            if _longest_variable(x) == _longest_variable(max(w, key=_longest_variable))
        ]
        for w in factorlist
    ]


def _ffilter_leftmost_sum(factorlist):  # noqa: ANN202, ANN001
    return [
        [
            x
            for x in w
            if sum(i for i in range(len(x)) if x.startswith("[", i))
            == min(sum(i for i in range(len(x)) if x.startswith("[", i)) for x in w)
        ]
        for w in factorlist
    ]


def _filterbracketings(factorlist, functionlist, tablecap):  # noqa: ANN202, ANN001
    def numcombinations(f):  # noqa: ANN202, ANN001
        return functools.reduce(lambda x, y: x * len(y), f, 1)

    if numcombinations(factorlist) > tablecap:
        for filterfunc in functionlist:
            factorlist = filterfunc(factorlist)
            if numcombinations(factorlist) <= tablecap:
                break
    return factorlist
