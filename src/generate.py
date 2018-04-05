from morphparser import test_paradigm


def run_paradigms(fittingparadigms, words, kbest=1, vbest=3, pprior=0, lms={},
                  numexamples=1, debug=False):
    if debug:
        print("Plausible paradigms:")
        for p in fittingparadigms:
            print(p.name)
    res = []
    # Quick filter out most paradigms
    for p in fittingparadigms[:kbest]:
        analyses = []
        print('paradigm', p.name)
        lm_score = lms[p.uuid]
        analyses.extend(test_paradigm(p, words, numexamples, pprior, lm_score))

        res.append((p.name, words, analyses))

    return res


def inflect_word(inp, paradigms, debug):
    print('inflect', inp, paradigms[1])
    res = []
    for line in inp:
        lemgram = line.strip()
        if debug:
            print('lemgram %s' % lemgram)

        # Quick filter out most paradigms
        fittingparadigms = [(pindex, p) for pindex, p in enumerate(paradigms)
                            if lemgram in p.members]
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
                    res.append((lemgram, words,
                                [(p, tuple([i[1] for i in inst[1:]]))]))
        if debug:
            print(words)

    return res
