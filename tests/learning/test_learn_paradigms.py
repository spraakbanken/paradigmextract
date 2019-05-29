import json
import os
from pextract import learnparadigms


def test1():
    table = ['stad', 'städer', 'stads']
    tags = [('msd', 'sg indef nom'), ('msd', 'pl indef nom'), ('msd', 'sg indef gen')]

    new_paradigms = learnparadigms([(table, tags)])
    assert len(new_paradigms) == 1


def test2():
    table1 = ['stad', 'städer', 'stads']
    table2 = ['bad', 'bäder', 'bads']
    tags = [('msd', 'sg indef nom'), ('msd', 'pl indef nom'), ('msd', 'sg indef gen')]

    new_paradigms = learnparadigms([(table1, tags), (table2, tags)])
    assert len(new_paradigms) == 1


def test3():
    table1 = ['stad', 'städer', 'stads']
    table2 = ['bad', 'bäder', 'bads']
    table3 = ['bord', 'bord', 'bords']
    tags = [('msd', 'sg indef nom'), ('msd', 'pl indef nom'), ('msd', 'sg indef gen')]

    new_paradigms = learnparadigms([(table1, tags), (table2, tags), (table3, tags)])
    assert len(new_paradigms) == 2


def test_all():
    join = os.path.join('/', *os.path.realpath(__file__).split('/')[:-2], 'testdata.json')
    with open(join) as fp:
        test_tables = json.load(fp)
        final_tables = []
        assert 9943 == len(test_tables)
        for table in test_tables:
            msds_ = table['msds']
            tags = []
            for msd in msds_:
                tags.append(('msd', msd))
            final_tables.append((table['wordforms'], tags))
        new_paradigms = learnparadigms(final_tables)
        # this value is transient, sometimes 551 sometimes 552 (for full testset)
        # it differs for the words "bortgallra", "bortkollra", "bortjaga", "bortsopa"
        # where they sometimes are all in the same paradigm and sometimes "bortjaga" is its own paradigm
        assert len(new_paradigms) == 551 or len(new_paradigms) == 552
