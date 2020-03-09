import sys

import paradigmextract.pextract as pextract


def split_tags(tags):
    spl = [tg.split(u',,') for tg in tags]

    newforms = []
    ctr = 1
    for form in spl:
        newelement = []
        for tagelement in form:
            if tagelement == u'':
                newelement.append((str(ctr), u'1'))
            elif u'=' in tagelement:
                splittag = tagelement.split(u'=')
                newelement.append((splittag[0], splittag[1]))
            else:
                newelement.append((tagelement, u'1'))
        newforms.append(newelement)
        ctr += 1
    return newforms


if __name__ == '__main__':
    lines = [l.strip() for l in sys.stdin]
    tables = []
    thistable = []
    thesetags = []
    for l in lines:
        if l == '':
            if len(thistable) > 0:
                splittags = split_tags(thesetags)
                tables.append((thistable, splittags))
                thistable = []
                thesetags = []
        else:
            if '\t' in l:
                _, tag, form = l.split('\t')
            else:
                form = l
                tag = ''
            thistable.append(form)
            thesetags.append(tag)

    if len(thistable) > 0:
        splittags = split_tags(thesetags)
        tables.append((thistable, splittags))

    learnedparadigms = pextract.learnparadigms(tables)
    for p in learnedparadigms:
        # print(str(p) + '\n\n')
        print('a paradigm')
