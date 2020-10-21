import functools
import math
import paradigmextract.paradigm as paradigm

from typing import List, Dict, Tuple, Set, Optional, Sequence, Any, Iterable, Union


class StringNgram:
    def __init__(
        self,
        stringset: List[str],
        alphabet: Optional[Set[str]] = None,
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
        ngrams = [
            x for word in self.stringset for x in self._letter_ngrams(word, order)
        ]
        self.ngramcounts: Dict = {}
        # Collect counts for n-grams and n-1 grams (mgrams)
        for ngram in ngrams:
            self.ngramcounts[ngram] = self.ngramcounts.get(ngram, 0) + 1
        mgrams = [
            x for word in self.stringset for x in self._letter_ngrams(word, order - 1)
        ]
        for mgram in mgrams:
            self.ngramcounts[mgram] = self.ngramcounts.get(mgram, 0) + 1

    def evaluate(self, string: str) -> float:
        s = "#" * (self.order - 1) + string + "#"
        return sum(self._getprob(x) for x in self._letter_ngrams(s, self.order))

    def _getprob(self, ngram) -> float:
        numerator = self.ngramcounts.get(ngram, 0) + self.ngramprior
        denominator = (
            self.ngramcounts.get(ngram[:-1], 0) + len(self.alphabet) * self.ngramprior
        )
        return math.log(numerator / float(denominator))

    @staticmethod
    def _letter_ngrams(word: str, n: int) -> List[str]:
        return ["".join(x) for x in zip(*[word[i:] for i in range(n)])]


def _paradigms_to_alphabet(paradigms: List[paradigm.Paradigm]) -> Set[str]:
    """Extracts all used symbols from an iterable of paradigms."""
    alphabet = set()
    for para in paradigms:
        for _, slot in para.slots:
            for word in slot:
                alphabet |= set(word)
    return alphabet - {"_"}


def _eval_vars(matches: List[str], lm: Tuple[float, List[StringNgram]]):
    if not lm[1]:
        # If paradigm does not have any instances.
        # This may happen if the paradigms are not updated
        # correctly.
        # TODO magic number. 0 is too high.
        return -100
    return sum(lm[1][midx].evaluate(m) for midx, m in enumerate(matches))


def eval_multiple_entries(
    p: paradigm.Paradigm,
    words: List[str],
    tags: Sequence[str] = (),
    baseform: bool = False,
) -> Set[Tuple[int, Any]]:
    """Returns a set of consistent variable assigment to all words."""
    wmatches: List[Set] = []
    for ix, w in enumerate(words):
        tag = tags[ix] if len(tags) > ix else ""
        wmatch = set()
        restrict = not tag and ix == 0 and baseform
        matches = p.match(w, constrained=False, tag=tag, baseform=restrict)
        for m in filter(lambda x: x is not None, matches):
            if not m:
                m = [(0, ())]  # Add dummy to show match is exact without vars
            for submatch in m:
                if len(submatch) > 0:
                    wmatch.add(submatch[1])
        wmatches.append(wmatch)

    def _union(x, y):
        return x & y

    return functools.reduce(_union, wmatches)


def eval_baseform(
    p: paradigm.Paradigm, word: str, possible_tags: Sequence[str] = ()
) -> Optional[List[str]]:
    """Returns a set of variable assigment for word in the first tag that matches"""

    def inner(tag: str = ""):
        baseform = not tag
        matches = p.match(word, constrained=False, tag=tag, baseform=baseform)
        for m in filter(lambda x: x is not None, matches):
            if not m:
                m = [(0, ())]  # Add dummy to show match is exact without vars
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


def build(
    paradigms, ngramorder: int, ngramprior: float
) -> Tuple[
    List[paradigm.Paradigm], int, Dict[str, Tuple[float, List[StringNgram]]], Set[str]
]:
    alphabet = _paradigms_to_alphabet(paradigms)

    numexamples = sum(map(lambda x: x.count, paradigms))

    lms = {}
    # Learn n-gram LM for each variable
    for p in paradigms:
        lms[p.uuid] = _lms_paradigm(p, alphabet, ngramorder, ngramprior)
    return paradigms, numexamples, lms, alphabet


def _lms_paradigm(
    paradigm_, alphabet, ngramorder, ngramprior
) -> Tuple[float, List[StringNgram]]:
    numvars = (len(paradigm_.slots) - 1) / 2
    slotmodels = []
    for v in range(0, int(numvars)):
        varinsts = paradigm_.slots[v * 2 + 1][1]
        model = StringNgram(
            varinsts, alphabet=alphabet, order=ngramorder, ngramprior=ngramprior
        )
        slotmodels.append(model)
    return numvars, slotmodels


def test_paradigms(
    inp: Union[List[str], Tuple[List[str], List[str]]],
    paradigms: List[paradigm.Paradigm],
    numexamples: int,
    lms: Dict[str, Tuple[float, List[StringNgram]]],
    pprior: float,
    match_all: bool = False,
    baseform: bool = False,
):
    tags: List = []
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
            p
            for p in paradigms
            if all(p.fits_paradigm(w, constrained=False) for w in words)
        ]

    fittingparadigms = list(
        filter(
            lambda p: eval_multiple_entries(p, words, tags, baseform=baseform),
            fittingparadigms,
        )
    )

    analyses = []
    # Calculate score for each possible variable assignment
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

    analyses.sort(reverse=True, key=lambda x: x[0])
    return analyses


def run_paradigms(
    fittingparadigms,
    words,
    kbest=1,
    pprior=0,
    lms=None,
    numexamples=1,
    baseform=False,
    tags=(),
) -> List[Tuple[float, paradigm.Paradigm, Iterable[str]]]:
    if lms is None:
        lms = {}
    analyses = []
    # Quick filter out most paradigms
    for p in fittingparadigms[:kbest]:
        lm_score = lms[p.uuid]
        analyses.extend(
            test_paradigm(
                p, words, numexamples, pprior, lm_score, tags=tags, baseform=baseform
            )
        )

    return analyses


def test_paradigm(
    para: paradigm.Paradigm,
    words: List[str],
    numexamples: int,
    pprior: float,
    lm_score: Tuple[float, List[StringNgram]],
    tags: Sequence = (),
    match_table=(),
    baseform=False,
) -> List[Tuple[float, paradigm.Paradigm, Iterable[str]]]:
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
    else:
        for v in variables:
            score = prior * pprior + len(words) * _eval_vars(v, lm_score)
            res.append((score, para, v))

    def match(_p, _v, table):
        try:
            return _p(*_v) == table
        except:
            return False

    if match_table:
        res = [(s, p, v) for (s, p, v) in res if match(p, v, match_table)]
    return res
