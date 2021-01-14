import json
import os
from paradigmextract.pextract import learnparadigms


def test1():
    table = ["stad", "städer", "stads"]
    tags = [("msd", "sg indef nom"), ("msd", "pl indef nom"), ("msd", "sg indef gen")]

    new_paradigms = learnparadigms([(table, tags)])
    assert len(new_paradigms) == 1


def test2():
    table1 = ["stad", "städer", "stads"]
    table2 = ["bad", "bäder", "bads"]
    tags = [("msd", "sg indef nom"), ("msd", "pl indef nom"), ("msd", "sg indef gen")]

    new_paradigms = learnparadigms([(table1, tags), (table2, tags)])
    assert len(new_paradigms) == 1


def test3():
    table1 = ["stad", "städer", "stads"]
    table2 = ["bad", "bäder", "bads"]
    table3 = ["bord", "bord", "bords"]
    tags = [("msd", "sg indef nom"), ("msd", "pl indef nom"), ("msd", "sg indef gen")]

    new_paradigms = learnparadigms([(table1, tags), (table2, tags), (table3, tags)])
    assert len(new_paradigms) == 2
