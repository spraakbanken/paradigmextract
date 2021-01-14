import functools
import json
import os
from paradigmextract.pextract import WordGraph


def get_lcs(table):
    wg = [WordGraph.from_string(x) for x in table]
    result = functools.reduce(lambda x, y: x & y, wg)
    return result.longestwords


def test1():
    table = ["stad", "städer", "stads"]
    lcs = get_lcs(table)
    assert len(lcs) == 1
    assert lcs[0] == "std"


def test_no_vars():
    table = ["xy", "z", "a"]
    lcs = get_lcs(table)
    assert len(lcs) == 0


def test2():
    table = ["apa", "apans", "xy"]
    lcs = get_lcs(table)
    assert len(lcs) == 0


def test3():
    table = [
        "svälter ihjäl",
        "svältes ihjäl",
        "svälts ihjäl",
        "svälte ihjäl",
        "svältes ihjäl",
        "svält ihjäl",
        "svälta ihjäl",
        "svältas ihjäl",
        "svält ihjäl",
        "svälts ihjäl",
        "svältande ihjäl",
        "svältandes ihjäl",
        "svält ihjäl",
        "ihjälsvält",
        "svälts ihjäl",
        "ihjälsvälts",
    ]
    lcs = get_lcs(table)
    assert set(lcs) == {"svält", "ihjäl"}


def test4():
    table = [
        "gytter",
        "gytters",
        "gyttret",
        "gyttrets",
        "gytter-",
        "gytter",
        "gytter-",
        "gytter",
        "gytter-",
    ]
    lcs = get_lcs(table)
    assert set(lcs) == {"gytte", "gyttr"}
