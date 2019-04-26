import sys

import paradigmextract.pextract as pextract

if __name__ == '__main__':
    lines = [l.strip() for l in sys.stdin]
    tables = []
    thistable = []
    thesetags = []
    for l in lines:
        if l == '':
            if len(thistable) > 0:
                splittags = pextract.split_tags(thesetags)
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
        splittags = pextract.split_tags(thesetags)
        tables.append((thistable, splittags))

    learnedparadigms = pextract.learnparadigms(tables)
    for p in learnedparadigms:
        # print(str(p) + '\n\n')
        print('a paradigm')
