import sys
from typing import List, Tuple

import paradigmextract.pextract as pextract


def split_tags(tags: List) -> List[List[Tuple[str, str]]]:
    spl = [tg.split(",,") for tg in tags]

    newforms = []
    ctr = 1
    for form in spl:
        newelement = []
        for tagelement in form:
            if tagelement == "":
                newelement.append((str(ctr), "1"))
            elif "=" in tagelement:
                splittag = tagelement.split("=")
                newelement.append((splittag[0], splittag[1]))
            else:
                newelement.append((tagelement, "1"))
        newforms.append(newelement)
        ctr += 1
    return newforms


if __name__ == "__main__":
    lines = [l.strip() for l in sys.stdin]
    tables: List[Tuple[List[str], List[List[Tuple[str, str]]]]] = []
    thistable: List[str] = []
    thesetags: List[str] = []
    for l in lines:
        if l == "":
            if thistable:
                splittags = split_tags(thesetags)
                tables.append((thistable, splittags))
                thistable = []
                thesetags = []
        else:
            if "\t" in l:
                _, tag, form = l.split("\t")
            else:
                form = l
                tag = ""
            thistable.append(form)
            thesetags.append(tag)

    if thistable:
        splittags = split_tags(thesetags)
        tables.append((thistable, splittags))

    learnedparadigms = pextract.learnparadigms(tables)
    for p in learnedparadigms:
        # print(str(p) + '\n\n')
        print("a paradigm")
