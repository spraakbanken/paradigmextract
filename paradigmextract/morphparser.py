"""Morph parser."""

import functools
import math
import operator
from collections.abc import Iterable, Sequence
from typing import Any, Optional, Union

from paradigmextract import paradigm


class StringNgram:  # noqa: D101
    def __init__(
        self,
        stringset: list[str],
        alphabet: Optional[set[str]] = None,
        order: int = 2,
        ngramprior: float = 0.01,
    ) -> None:
        """Read a set of strings and create an n-gram model."""
        self.stringset = ["#" * (order - 1) + s + "#" for s in stringset]
        self.alphabet = {char for s in self.stringset for char in s}
        self.order = order
        self.ngramprior = ngramprior
        if alphabet:
            self.alphabet |= alphabet
        ngrams = [x for word in self.stringset for x in self._letter_ngrams(word, order)]
        self.ngramcounts: dict = {}
        # Collect counts for n-grams and n-1 grams (mgrams)
        for ngram in ngrams:
            self.ngramcounts[ngram] = self.ngramcounts.get(ngram, 0) + 1
        mgrams = [x for word in self.stringset for x in self._letter_ngrams(word, order - 1)]
        for mgram in mgrams:
            self.ngramcounts[mgram] = self.ngramcounts.get(mgram, 0) + 1

    def evaluate(self, string: str) -> float:  # noqa: D102
        s = "#" * (self.order - 1) + string + "#"
        return sum(self._getprob(x) for x in self._letter_ngrams(s, self.order))

    def _getprob(self, ngram) -> float:  # noqa: ANN001
        numerator = self.ngramcounts.get(ngram, 0) + self.ngramprior
        denominator = self.ngramcounts.get(ngram[:-1], 0) + len(self.alphabet) * self.ngramprior
        return math.log(numerator / float(denominator))

    @staticmethod
    def _letter_ngrams(word: str, n: int) -> list[str]:
        return ["".join(x) for x in zip(*[word[i:] for i in range(n)])]


def _paradigms_to_alphabet(paradigms: list[paradigm.Paradigm]) -> set[str]:
    """Extract all used symbols from an iterable of paradigms."""
    alphabet = set()
    for para in paradigms:
        for _, slot in para.slots:
            for word in slot:
                alphabet |= set(word)
    return alphabet - {"_"}


def _eval_vars(matches: list[str], lm: tuple[float, list[StringNgram]]):  # noqa: ANN202
    if not lm[1]:
        # If paradigm does not have any instances.
        # This may happen if the paradigms are not updated
        # correctly.
        # TODO magic number. 0 is too high.
        return -100
    return sum(lm[1][midx].evaluate(m) for midx, m in enumerate(matches))


def eval_multiple_entries(
    p: paradigm.Paradigm,
    words: list[str],
    tags: Sequence[str] = (),
    baseform: bool = False,
) -> set[tuple[int, Any]]:
    """Return a set of consistent variable assignment to all words."""
    wmatches: list[set] = []
    for ix, w in enumerate(words):
        tag = tags[ix] if len(tags) > ix else ""
        wmatch = set()
        restrict = not tag and ix == 0 and baseform
        matches = p.match(w, constrained=False, tag=tag, baseform=restrict)
        for m in filter(lambda x: x is not None, matches):
            if not m:
                m = [(0, ())]  # Add dummy to show match is exact without vars  # noqa: PLW2901
            for submatch in m:
                if len(submatch) > 0:
                    wmatch.add(submatch[1])
        wmatches.append(wmatch)

    def _union(x, y):  # noqa: FURB118, ANN202, ANN001
        return x & y

    return functools.reduce(_union, wmatches)


def eval_baseform(
    p: paradigm.Paradigm, word: str, possible_tags: Sequence[str] = ()
) -> Optional[list[str]]:
    """Return a set of variable assignment for word in the first tag that matches."""

    def inner(tag: str = ""):  # noqa: ANN202
        baseform = not tag
        matches = p.match(word, constrained=False, tag=tag, baseform=baseform)
        for m in filter(lambda x: x is not None, matches):
            if not m:
                m = [(0, ())]  # Add dummy to show match is exact without vars  # noqa: PLW2901
            for submatch in m:
                if len(submatch) > 0:
                    return submatch[1]
        return None

    for possible_tag in possible_tags:
        result = inner(tag=possible_tag)
        if result is not None:
            return list(result)
    if not possible_tags:
        result = inner()
        return list(result) if result is not None else None
    return None


def build(  # noqa: D103
    paradigms,  # noqa: ANN001
    ngramorder: int,
    ngramprior: float,
) -> tuple[list[paradigm.Paradigm], int, dict[str, tuple[float, list[StringNgram]]], set[str]]:
    alphabet = _paradigms_to_alphabet(paradigms)

    numexamples = sum(x.count for x in paradigms)

    lms = {p.uuid: _lms_paradigm(p, alphabet, ngramorder, ngramprior) for p in paradigms}
    return paradigms, numexamples, lms, alphabet


def _lms_paradigm(
    paradigm_,  # noqa: ANN001
    alphabet,  # noqa: ANN001
    ngramorder,  # noqa: ANN001
    ngramprior,  # noqa: ANN001
) -> tuple[float, list[StringNgram]]:
    numvars = (len(paradigm_.slots) - 1) / 2
    slotmodels = []
    for v in range(int(numvars)):
        varinsts = paradigm_.slots[v * 2 + 1][1]
        model = StringNgram(varinsts, alphabet=alphabet, order=ngramorder, ngramprior=ngramprior)
        slotmodels.append(model)
    return numvars, slotmodels


def test_paradigms(  # noqa: ANN201, D103
    inp: Union[list[str], tuple[list[str], list[str]]],
    paradigms: list[paradigm.Paradigm],
    numexamples: int,
    lms: dict[str, tuple[float, list[StringNgram]]],
    pprior: float,
    match_all: bool = False,
    baseform: bool = False,
):
    tags: list = []
    # sourcery skip: no-conditionals-in-tests
    if isinstance(inp, tuple):
        words, tags = inp
    else:
        words = inp

    if len(words) == 0:
        return []

    # Quick filter out most paradigms
    if tags:
        table = list(zip(words, tags))
        fittingparadigms = [
            p
            for p in paradigms
            if all(p.fits_paradigm(w, constrained=False, tag=t) for w, t in table)
        ]
    else:
        fittingparadigms = [
            p for p in paradigms if all(p.fits_paradigm(w, constrained=False) for w in words)
        ]

    fittingparadigms = list(
        filter(
            lambda p: eval_multiple_entries(p, words, tags, baseform=baseform),
            fittingparadigms,
        )
    )

    analyses = []
    # Calculate score for each possible variable assignment
    # sourcery skip: no-loop-in-tests
    for p in fittingparadigms:
        lm_score = lms[p.uuid]
        match_table = list(zip(words, tags)) if match_all else []
        analyses.extend(
            test_paradigm(
                p,
                words,
                numexamples,
                pprior,
                lm_score,
                tags=tags,
                match_table=match_table,
                baseform=baseform,
            )
        )

    analyses.sort(reverse=True, key=operator.itemgetter(0))
    return analyses


def run_paradigms(  # noqa: D103
    fittingparadigms,  # noqa: ANN001
    words,  # noqa: ANN001
    kbest=1,  # noqa: ANN001
    pprior=0,  # noqa: ANN001
    lms=None,  # noqa: ANN001
    numexamples=1,  # noqa: ANN001
    baseform=False,  # noqa: ANN001
    tags=(),  # noqa: ANN001
) -> list[tuple[float, paradigm.Paradigm, Iterable[str]]]:
    if lms is None:
        lms = {}
    analyses = []
    # Quick filter out most paradigms
    for p in fittingparadigms[:kbest]:
        lm_score = lms[p.uuid]
        analyses.extend(
            test_paradigm(p, words, numexamples, pprior, lm_score, tags=tags, baseform=baseform)
        )

    return analyses


def test_paradigm(  # noqa: D103
    para: paradigm.Paradigm,
    words: list[str],
    numexamples: int,
    pprior: float,
    lm_score: tuple[float, list[StringNgram]],
    tags: Sequence = (),
    match_table=(),  # noqa: ANN001
    baseform=False,  # noqa: ANN001
) -> list[tuple[float, paradigm.Paradigm, Iterable[str]]]:
    res = []
    try:
        prior = math.log(para.count / float(numexamples))
    except ValueError:
        prior = 0
    # All possible instantiations
    variables = eval_multiple_entries(para, words, tags, baseform=baseform)
    if len(variables) == 0:
        score = prior
        return [(score, para, ())]
    for v in variables:
        score = prior * pprior + len(words) * _eval_vars(v, lm_score)
        res.append((score, para, v))

    def match(_p, _v, table):  # noqa: ANN202, ANN001
        try:
            return _p(*_v) == table
        except Exception:
            return False

    if match_table:
        res = [(s, p, v) for (s, p, v) in res if match(p, v, match_table)]
    return res
