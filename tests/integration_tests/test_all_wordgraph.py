import functools
import json
import os
from paradigmextract.pextract import WordGraph


def get_lcs(table):
    wg = [WordGraph.from_string(x) for x in table]
    result = functools.reduce(lambda x, y: x & y, wg)
    return result.longestwords


def test_all():
    join = os.path.join(
        "/", *os.path.realpath(__file__).split("/")[:-2], "testdata.json"
    )
    with open(join) as fp:
        test_tables = json.load(fp)
        for table in test_tables:
            lcs = get_lcs(table["wordforms"])
            assert lcs is not None
