import functools
import operator

from paradigmextract.pextract import WordGraph


def get_lcs(table):
    wg = [WordGraph.from_string(x) for x in table]
    result = functools.reduce(operator.and_, wg)
    return result.longestwords


def test_all(test_tables: list[dict[str, list[str]]]):
    for table in test_tables:
        lcs = get_lcs(table["wordforms"])
        assert lcs is not None
