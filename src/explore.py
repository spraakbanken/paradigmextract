# coding:utf-8
import codecs
from collections import Counter
import generate
import paradigm as P
import re
import readline
import sys
""" Show statistics and facts about a number of paradigms
    (Adapted for saol identifiers ("ord.1_0")
    Usage:
      # Show statistcics
      > Stats

      # Show single paradigms
      > Singlar

      # Show statistics about a word ("ko")
      > ko
      > Stats ko

      # Inflect a known word
      > Böj ko

      # Inflect a word like another word
      > ko, kalv
      > Böj ko, kalv

      # Check wheather a word inflects like another word
      > ? ko, kalv
      > ko, kalv ?
      > Böj ko, kalv?

      # Inspect table
      > Tabell ko
"""


def count(paradigmfile):
    " Count the number of words for each paradigm "
    c = Counter()
    for line in paradigmfile:
        infl, words = line.split('\t')
        words = words.split('#')
        group = span(words)
        c[group] += 1
    return c


def span(words):
    " Divide frequency counts into spans "
    last = None
    limits = [10, 20, 50, 100, 200, 500, 1000, 10000]
    for lim in limits:
        if len(words) < lim:
            return last or len(words)
        last = lim
    return limits[-1]


def find_singles(paradigmfile):
    " Find paradigms with only one word "
    singles = []
    for line in paradigmfile:
        infl, words = line.split('\t')
        words = words.split('#')
        if len(words) == 1:
            singles.append(re.search('0=(.*?),,', words[0]).group(1))
    return singles


def make_innerwordregexp(word):
    " Make a regexp for saol identifiers "
    word = word.strip()
    if '.' in word:
        rex = word.replace('.', '\.')
    else:
        rex = word+'\..'
    if '_' not in word:
        rex += '_.'
    return rex


def make_wordregexp(word):
    " Make a regexp for saol identifiers, surroneded by separators "
    rex = make_innerwordregexp(word)
    return '0=('+rex+'),,'


def show_word(word, parafile):
    " Show information about a words inflection "
    result = findstats(parafile, word)
    if not result:
        print 'Kunde inte hitta %s\n' % word
        return
    for form, neighbours in result:
        print u'%s böjs som %s andra ord' % (form, len(neighbours)),
        if neighbours:
            print ', tex\n\t%s' % '\n\t'.join(neighbours[:10])
        else:
            print ''
        print


def findstats(inpfile, word):
    " Find statistics about a word and its paradigm "
    word = word.strip()
    result = []
    for line in inpfile:
        match = re.search(make_wordregexp(word), line)
        if match is not None:
            infl, words = line.split('\t')
            neighbours = words.split('#')
            neighbours = [re.search('0=(.*?),,', n).group(1) for n in neighbours]
            result.append((match.group(1), [n for n in neighbours if not n.startswith(word)]))
    return result


def make_wordlemgrams(word, lemgram):
    " Prepare the word and lemgram to be searched for "
    word = word.split('.')[0]
    res = []
    if '.' not in lemgram:
        lemgrams = ['%s.%s' % (lemgram, x) for x in range(5)]
    else:
        lemgrams = [lemgram]
    likes = []
    for lemgram in lemgrams:
        if '_' not in lemgram:
            likes.extend([lemgram+'_'+x for x in ['', '?', '0', '1', 'M']])
        else:
            likes.append(lemgram)
    for like in likes:
        res.append((word, like))
    return res


def inflect_one(word, paradigms):
    " Inflect a word according to its paradigm description "
    res = make_wordlemgrams(word, word)
    have_printed = False
    for (word, like) in res:
        ans = generate.inflect_word([like], paradigms, False)
        printed = print_inflection(ans)
        have_printed = have_printed or printed
    if not have_printed:
        print u'Vet inte hur man böjer %s' % word
        print


def inflect_like(word1, word2, paradigms):
    " Inflect word1 the same way that word2 is inflected"
    res = make_wordlemgrams(word1, word2)
    have_printed = False
    for (word, like) in res:
        ans = generate.test_paradigms(['%s %s' % (word, like)], paradigms, False)
        printed = print_inflection(ans)
        have_printed = have_printed or printed
    if not have_printed:
        print u'Kan inte böja %s som %s' % (word1, word2)
        print


def print_inflection(ans):
    " Print an inflection and report whether anything has been printed "
    printed = False
    for lemgram, words, analyses in ans:
        for aindex, (p, v) in enumerate(analyses):
            try:
                table = p(*v)  # Instantiate table with vars from analysis
                print lemgram, ':'
                for form, msd in table:
                    # if form in words:
                    #     form = "*" + form + "*"
                    msdprint = ','.join([m[0] + '=' + m[1] for m in msd])
                    print (form + '\t' + msdprint).encode("utf-8")
                print
                printed = True
            except:
                # fails if the inflection does not work (instantiation fails)
                pass
    return printed


def loop():
    " The main loop "
    parafile = sys.argv[1]
    paradigms = P.load_file(parafile)
    parafile = codecs.open(parafile, encoding='utf8').readlines()
    readline.parse_and_bind('tab: complete')
    while True:
        inp = raw_input("skriv ett ord:").decode('utf8')
        # Show single paradigms
        if inp.strip() == 'Singlar':
            singels = find_singles(parafile)
            print '\n'.join(singels)
            print
            continue

        # Show paradigm statistics
        if inp.strip() == 'Stats':
            print '%s paradigm\n' % len(parafile)
            print 'Ord per paradigm'
            for words, num in sorted(list(count(parafile).items())):
                if words >= 10:
                    words = '%s+' % words
                print words, '\t', num
            print
            continue

        # Show word statistic
        show = re.search('Show\s(.*\S)', inp)
        if show is not None:
            show_word(show.group(1), parafile)
            continue

        # Does x inflect as y?
        show_a = re.search('\?(.*),(.*)', inp)
        show_b = re.search('(.*),(.*)\?', inp)
        show_c = re.search(u'Böj\s(.*),(.*)\s*\?', inp)
        show = show_a or show_b or show_c
        if show is not None:
            word1 = show.group(1).strip()
            word2 = show.group(2).strip()
            print u'Böjs %s som %s?' % (word1, word2)
            same = False
            for line in parafile:
                re1 = make_wordregexp(word1)
                re2 = make_wordregexp(word2)
                match = re.search(re1+'.*'+re2, line)
                if match is not None:
                    same = True
                    break
                match = re.search(re2+'.*'+re1, line)
                if match is not None:
                    same = True
                    break
            print 'Ja' if same else 'Nej'
            print
            continue

        # Inflect x as y
        inflectlike = False
        inflect = re.search(u'Böj (.*), (.*)', inp)
        splitted = inp.split(',')
        if inflect is not None:
            word1 = inflect.group(1)
            word2 = inflect.group(2)
            inflectlike = True
        elif len(splitted) > 1:
            word1 = splitted[0]
            word2 = splitted[1]
            inflectlike = True
        if inflectlike:
            print u'Böj %s som %s' % (word1, word2)
            inflect_like(word1, word2, paradigms)
            continue

        # Inflect a known word
        inflect = re.search(u'Böj (.*)', inp)
        if inflect is not None:
            word = inflect.group(1)
            inflect_one(word, paradigms)
            continue

        # Show the table for a known word
        table = re.search(u'Tabell (.*)', inp)
        if table is not None:
            word = table.group(1)
            for p in paradigms:
                match = re.search(',,(%s),,' % make_innerwordregexp(word), ',,%s,,' % ',,'.join(p.members))
                if match is not None:
                    print match.group(1), ':'
                    for f in p.forms:
                        print unicode(f).replace('::', '\t').encode('utf-8')
                    print
            print
            continue
        # Show stats for word
        show_word(inp, parafile)
        continue


if __name__ == "__main__":
    loop()
