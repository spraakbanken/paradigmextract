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
import getopt
import functools
import math
import paradigm
import sys


class stringngram:

    def __init__(self, stringset, alphabet=None, order=2, ngramprior=0.01):
        """Read a set of strings and create an n-gram model."""
        self.stringset = [u'#'*(order-1) + s + u'#' for s in stringset]
        self.alphabet = {char for s in self.stringset for char in s}
        self.order = order
        self.ngramprior = ngramprior
        if alphabet:
            self.alphabet |= alphabet
        ngrams = [x for word in self.stringset for x in self._letter_ngrams(word, order)]
        self.ngramcounts = {}
        # Collect counts for n-grams and n-1 grams (mgrams)
        for ngram in ngrams:
            self.ngramcounts[ngram] = self.ngramcounts.get(ngram, 0) + 1
        mgrams = [x for word in self.stringset for x in self._letter_ngrams(word, order-1)]
        for mgram in mgrams:
            self.ngramcounts[mgram] = self.ngramcounts.get(mgram, 0) + 1

    def evaluate(self, string):
        s = u'#'*(self.order-1) + string + u'#'
        return sum(self._getprob(x) for x in self._letter_ngrams(s, self.order))

    def _getprob(self, ngram):
        numerator = self.ngramcounts.get(ngram, 0) + self.ngramprior
        denominator = self.ngramcounts.get(ngram[:-1], 0) + len(self.alphabet) * self.ngramprior
        return math.log(numerator/float(denominator))

    def _letter_ngrams(self, word, n):
        return [''.join(x) for x in zip(*[word[i:] for i in range(n)])]


def paradigms_to_alphabet(paradigms):
    """Extracts all used symbols from an iterable of paradigms."""
    alphabet = set()
    for paradigm in paradigms:
        for idx, (is_var, slot) in enumerate(paradigm.slots):
            for word in slot:
                alphabet |= set(word)
    return alphabet - {'_'}


def extend_alphabet(paradigm, alphabet):
    """Extracts all used symbols from an iterable of one paradigm."""
    for idx, (is_var, slot) in enumerate(paradigm.slots):
        for word in slot:
            alphabet |= set(word)
    return alphabet - {'_'}


def eval_vars(matches, lm):
    return sum(lm[1][midx].evaluate(m) for midx, m in enumerate(matches))
    # TODO fix
    # except:
    #     return 1
    # if lm:
    #     return sum(lm[1][midx].evaluate(m) for midx, m in enumerate(matches))
    # else:
    #     return 1


def eval_multiple_entries(p, words, tags=[], baseform=False):
    """Returns a set of consistent variable assigment to all words."""
    wmatches = []
    # print('match', words, 'tags', tags)
    for ix, w in enumerate(words):
        tag = tags[ix] if len(tags) > ix else ''
        wmatch = set()
        # TODO this parsing should already be done
        # msd = [tuple(x.split('=')) for x in tag.split(',,') if tag]
        # print('ix', ix)
        # print('word', w)
        # print('tag', tag)
        # TODO when to exclude tag???
        #if not tag or tag[0][1] != 'identifier':
        restrict = not tag and ix == 0 and baseform
        for m in filter(lambda x: x is not None, p.match(w, constrained=False, tag=tag, baseform=restrict)):
            if m == []:
                m = [(0, ())]  # Add dummy to show match is exact without vars
            for submatch in m:
                if len(submatch) > 0:
                    wmatch.add(submatch[1])
        wmatches.append(wmatch)
    consistentvars = functools.reduce(lambda x, y: x & y, wmatches)
    return consistentvars


def main(argv):

    options, remainder = getopt.gnu_getopt(argv[1:], 'tk:n:p:dr:c', ['tables','kbest','ngram','prior','debug','pprior','choose'])

    print_tables, kbest, ngramorder, ngramprior, debug, pprior,choose = False, 1, 3, 0.01, False, 1.0, False
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
    paras, numexamples, lms, alphabet = build(sys.argv[1], ngramorder, ngramprior)
    res = []
    for line in inp:
       res.append(test_paradigms(line, paras, numexamples, lms, print_tables, debug, pprior, choose))

    for words, analyses in res:
        # Print all analyses + optionally a table
        for aindex, (score, p, v) in enumerate(analyses):
            if aindex >= kbest:
                break
            wordformlist = []
            varstring = '(' + ','.join([str(feat) + '=' + val for feat,val in zip(range(1,len(v)+1), v)]) + ')'
            table = p(*v)          # Instantiate table with vars from analysis
            baseform = table[0][0]
            matchtable = [(form, msd) for form, msd in table if form in words]
            wordformlist = [form +':' + baseform + ',' + ','.join([m[0] + '=' + m[1] for m in msd]) for form, msd in matchtable]
            # print((unicode(score) + ' ' + p.name + ' ' + varstring + ' ' + '#'.join(wordformlist)).encode("utf-8"))
            if print_tables:
                for form, msd in table:
                    if form in words:
                        form = "*" + form + "*"
                    msdprint = ','.join([m[0] + '=' + m[1] for m in msd])
                    # print((form + '\t' + msdprint).encode("utf-8"))

            if debug:
               print("Members:", ", ".join([p(*[var[1] for var in vs])[0][0] for vs in p.var_insts]))
        print


def build(inpfile, ngramorder, ngramprior, small=False, lexicon='', inpformat='pfile', pos=''):
    if inpformat == 'pfile':
        paradigms = paradigm.load_p_file(inpfile, lex=lexicon) # [(occurrence_count, name, paradigm),...,]
    elif inpformat == 'jsonfile':
        paradigms = paradigm.load_json_file(inpfile, lex=lexicon, pos=pos)
    elif inpformat == 'json':
        paradigms = paradigm.load_json(inpfile, lex=lexicon, pos=pos)
    alphabet = paradigms_to_alphabet(paradigms)

    numexamples = sum(map(lambda x: x.count, paradigms))

    lms = {}
    # Learn n-gram LM for each variable
    for p in paradigms:
        lms_paradigm(p, lms, alphabet, ngramorder, ngramprior)
        if small:
            print('shrink')
            p.shrink()
    return paradigms, numexamples, lms, alphabet


def lms_paradigm(paradigm, lms, alphabet, ngramorder, ngramprior):
    numvars = (len(paradigm.slots) - 1)/2
    slotmodels = []
    for v in range(0, int(numvars)):
        varinsts = paradigm.slots[v*2+1][1]
        model = stringngram(varinsts, alphabet=alphabet, order=ngramorder, ngramprior=ngramprior)
        slotmodels.append(model)
    lms[paradigm.uuid] = (numvars, slotmodels)


def test_paradigms(inp, paradigms, numexamples, lms, print_tables, debug,
                   pprior, choose=False, returnempty=True, match_all=False,
                   baseform=False):
    tags = []
    # print('test', len(paradigms), paradigms)
    if choose:
        word, lemgram = inp.strip().split()
        words = [word]
    elif type(inp) == tuple:
        words, tags = inp
    else:
        words = inp  # line.strip().split()

    # print('input', words, 'tags', tags)
    if len(words) == 0:
        return []

    if choose:
        # print('choose', lemgram)
        fittingparadigms = [p for p in paradigms if lemgram in p.members]
        #fittingparadigms = [(pindex, p) for pindex, p in enumerate(paradigms) if p.name==inppara]
    else:
        # Quick filter out most paradigms
        if tags:
            table = list(zip(words, tags))
            fittingparadigms = [p for p in paradigms\
                                if all(p.fits_paradigm(w, constrained=False, tag=t) for w,t in table)]
            # for p in paradigms:
            #    ok = all(p.fits_paradigm(w, constrained=False, tag=t) for w,t in table)
            #    print('p',p, 'ok?',ok)
        else:
            fittingparadigms = [p for p in paradigms if all(p.fits_paradigm(w, constrained=False) for w in words)]
        # print('fitting', len(fittingparadigms))

    # print('fitting', len(fittingparadigms))
    # print('test', words, 'tags', tags)
    fittingparadigms = list(filter(lambda p: eval_multiple_entries(p, words, tags, baseform=baseform), fittingparadigms))
    # print('now fitting', len(fittingparadigms))
    # print('tested', words, 'tags', tags)
    # print('fitting', len(fittingparadigms))
    if debug:
    # Quick filter out most paradigms
        print("Plausible paradigms:")
        for p in fittingparadigms:
            print(p.name)

    analyses = []
    # Calculate score for each possible variable assignment
    for p in fittingparadigms:
        # print('test', p)
        lm_score = lms[p.uuid]
        match_table = list(zip(words, tags)) if match_all else []
        # print('match_table', match_table)
        # print('test', p, words, baseform)
        analyses.extend(test_paradigm(p, words, numexamples, pprior,
                                      lm_score, tags=tags,
                                      match_table=match_table,
                                      baseform=baseform))

    analyses.sort(reverse=True, key=lambda x: x[0])
    # if analyses or returnempty:
    #     res.append(analyses)
    return analyses


def run_paradigms(fittingparadigms, words, kbest=1, vbest=3, pprior=0, lms={},
                  numexamples=1, debug=False, baseform=False):
    if debug:
        print("Plausible paradigms:")
        for p in fittingparadigms:
            print(p.name)
    analyses = []
    # Quick filter out most paradigms
    for p in fittingparadigms[:kbest]:
        lm_score = lms[p.uuid]
        analyses.extend(test_paradigm(p, words, numexamples, pprior, lm_score,
                                      baseform=baseform))

    return analyses


def test_paradigm(p, words, numexamples, pprior, lm_score, tags=[],
                  match_table=[], baseform=False):
    res = []
    # print(p.name)
    # print("p.count", p.count)
    # print('words', words)
    prior = math.log(p.count/float(numexamples))
    vars = eval_multiple_entries(p, words, tags, baseform=baseform)  # All possible instantiations
    if len(vars) == 0:
        # TODO this probably never happens, since p list is already filtered on
        # eval_multiple_entries
        # Word matches
        score = prior
        res.append((score, p, ()))
    else:
        for v in vars:
            score = prior * pprior + len(words) * eval_vars(v, lm_score)
            res.append((score, p, v))

    def match(p, v, table):
        try:
            # print('table?', p(*v))
            return p(*v) == table
        except:
            return False

    if match_table:
        # print('Compare tables')
        # print('Goal %s' % match_table)
        res = [(s, p, v) for (s, p, v) in res if match(p, v, match_table)]
    return res



if __name__ == "__main__":
    main(sys.argv)
