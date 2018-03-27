import math
from morphparser import eval_multiple_entries, eval_vars
import paradigm as P
import sys

debug = False

def main(inp, parafile):
    paradigms = P.load_p_file(parafile) # [(occurrence_count, name, paradigm),...,]
    res = test_paradigms(inp, paradigms, debug)
    for lemgram, words, analyses in res:
        for aindex, (score, p, v) in enumerate(analyses):
            table = p(*v)          # Instantiate table with vars from analysis
            for form, msd in table:
                # if form in words:
                #     form = "*" + form + "*"
                msdprint = ','.join([m[0] + '=' + m[1] for m in msd])
                print((form + '\t' + msdprint).encode("utf-8"))
            print


def test_member_paradigms(inp, paradigms, debug, kbest=1, vbest=3, pprior=0, lms=[], numexamples=1):
    def is_fitting(p, match):
        return any(l in p.members for l in match)
    return test_paradigms(inp, paradigms, debug, fitting=is_fitting,
                          kbest=kbest, vbest=vbest, pprior=pprior, lms=lms,
                          numexamples=numexamples)


def test_name_paradigms(inp, paradigms, debug, kbest=1, vbest=3, pprior=0, lms=[], numexamples=1):
    def is_fitting(p, match):
        print('test',p.name, match)
        return any(l == p.name for l in match)

    return test_paradigms(inp, paradigms, debug, fitting=is_fitting,
                          kbest=kbest, vbest=vbest, pprior=pprior, lms=lms,
                          numexamples=numexamples)


def test_paradigms(inp, paradigms, debug, fitting=None, kbest=1, vbest=3, pprior=0, lms=[], numexamples=1):
    res = []
    if fitting is None:
        fitting = lambda p, match: True

    for line in inp:
        print('line', line)
        word, lemgram = line.strip().split('\t')
        lemgrams = lemgram.split('|')
        if debug:
           print('word %s, lemgram %s' % (word, lemgram))
        words = [word]
        if len(words) == 0:
            continue

        print('all paradigms', [(pindex, p.members[0]) for pindex, p in enumerate(paradigms)])
        fittingparadigms = [(pindex, p) for pindex, p in enumerate(paradigms) if fitting(p, lemgrams)]
        if debug:
        # Quick filter out most paradigms
            print("Plausible paradigms:")
            for pnum, p in fittingparadigms:
                print(pnum, p.name)


        # TODO Calculate score for each possible variable assignment
        for pindex, p in fittingparadigms[:kbest]:
            analyses = []
            print('paradigm', pindex, p.name)
            print('eval entries', p, words)
            vars = eval_multiple_entries(p, words) # All possible instantiations
            print('vars', vars)
            prior = math.log(p.count/float(numexamples))
            if len(vars) == 0:
                # Word matches
                score = prior
                analyses.append((score, p, ()))
            else:
                for v in list(vars)[:vbest]:
                    print('pindex',pindex,len(lms))
                    lm_score = 0 if len(lms) <= pindex else lms[pindex]
                    score = prior * pprior + len(words) * eval_vars(v, lm_score)
                    print('vars score',eval_vars(v, lm_score))
                    print('add another v', v)
                    analyses.append((score, p, v))

            if len(lemgrams) == 1:
                example = lemgram
            else:
                example = p.name

            res.append((example, words, analyses))
    return res


def inflect_word(inp, paradigms, debug):
    print('inflect', inp, paradigms[1])
    res = []
    for line in inp:
        lemgram = line.strip()
        if debug:
           print('lemgram %s' % lemgram)

        # Quick filter out most paradigms
        fittingparadigms = [(pindex, p) for pindex, p in enumerate(paradigms) if lemgram in p.members]
        if debug:
            print("Plausible paradigms:")
            for pnum, p in fittingparadigms:
                print(pnum, p.name)
                print('slots', p.var_insts[0])

        words = []
        for pnum, p in fittingparadigms:
            for inst in p.var_insts:
              if inst[0][1] == lemgram:
                  words.append(inst[0][1].split('.')[0])
                  if debug:
                      print('v', tuple([i[1] for i in inst[1:]]))
                  # Use the variable instatiations from the paradigm file
                  res.append((lemgram, words, [(p, tuple([i[1] for i in inst[1:]]))]))
        if debug:
            print(words)

    return res


# def make_new_paradigm(inflectiontable):
#     print('learn', thistable, thesetags)
#     paradigm = pex.learnparadigms([(thistable, thesetags)])[0]
#     #print(paradigm.var_insts)
#     #print(paradigm.name)
#     #for form in paradigm.forms:
#     #     print(form.form)
#     #     print(form.msd)
#     #     print('s',str(form))
#     return paradigm






if __name__ == "__main__":
    inp = iter(lambda: sys.stdin.readline().decode('utf-8'), '')
    main(inp)
    # paradigms = P.load_file(sys.argv[1]) # [(occurrence_count, name, paradigm),...,]
    # ans = inflect_word(inp, paradigms, True)
    # for lemgram, words, analyses in ans:
    #     for aindex, (p, v) in enumerate(analyses):
    #             table = p(*v)          # Instantiate table with vars from analysis
    #             print lemgram, ':'
    #             for form, msd in table:
    #                 # if form in words:
    #                 #     form = "*" + form + "*"
    #                 msdprint = ','.join([m[0] + '=' + m[1] for m in msd])
    #                 print (form + '\t' + msdprint).encode("utf-8")
    #             print
