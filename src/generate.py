from morphparser import eval_multiple_entries
import paradigm as P
import pextract.pextract as pex
import sys

debug = False

def main(inp, parafile):
    paradigms = P.load_file(parafile) # [(occurrence_count, name, paradigm),...,]
    res = test_paradigms(inp, paradigms, debug)
    for lemgram, words, analyses in res:
        for aindex, (p, v) in enumerate(analyses):
            table = p(*v)          # Instantiate table with vars from analysis
            for form, msd in table:
                # if form in words:
                #     form = "*" + form + "*"
                msdprint = ','.join([m[0] + '=' + m[1] for m in msd])
                print((form + '\t' + msdprint).encode("utf-8"))
            print



def test_paradigms(inp, paradigms, debug, kbest=1, vbest=3):
    res = []
    for line in inp:
        word, lemgram = line.strip().split('\t')
        lemgrams = lemgram.split('|')
        if debug:
           print('word %s, lemgram %s' % (word, lemgram))
        words = [word]
        if len(words) == 0:
            continue

        fittingparadigms = [(pindex, p) for pindex, p in enumerate(paradigms) if any(l in p.members for l in lemgrams)]
        if debug:
        # Quick filter out most paradigms
            print("Plausible paradigms:")
            for pnum, p in fittingparadigms:
                print(pnum, p.name)


        # Calculate score for each possible variable assignment
        for pindex, p in fittingparadigms[:kbest]:
            analyses = []
            print('paradigm', pindex, p.name)
            vars = eval_multiple_entries(p, words) # All possible instantiations
            if len(vars) == 0:
                # Word matches
                analyses.append((p, ()))
            else:
                for v in list(vars)[:vbest]:
                    print('add another v', v)
                    analyses.append((p, v))

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
