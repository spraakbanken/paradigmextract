from paradigmextract.morphparser import eval_multiple_entries
from paradigmextract.paradigm import Paradigm


def test_1():
    form_msds = [
        ("1", ("msd", "sg indef nom")),
        ("1+n", ("msd", "pl def nom")),
        ("1+ns", ("msd", "sg def gen")),
    ]
    var_insts = [[("1", "apa")]]
    p = Paradigm(form_msds, var_insts)
    words = ["apa", "apan", "apans"]
    variables = eval_multiple_entries(p, words, baseform=True)
    assert {("apa",)} == variables


def test_2():
    form_msds = [("apa", ("msd", "sg indef nom")), ("bepa", ("msd", "pl def nom"))]
    p = Paradigm(form_msds, [[]])
    words = ["apa"]
    variables = eval_multiple_entries(p, words, baseform=True)
    assert {()} == variables


def test_3():
    form_msds = [("apa", ("msd", "sg indef nom")), ("bepa", ("msd", "pl def nom"))]
    p = Paradigm(form_msds, [[]])
    tags = [("msd", "sg indef nom"), ("msd", "pl def nom")]

    # exact table works
    variables = eval_multiple_entries(p, ["apa", "bepa"], tags=tags, baseform=False)
    assert {()} == variables

    # conflicting table fails
    variables = eval_multiple_entries(p, ["apa", "other"], tags=tags)
    assert set() == variables

    # more forms than paradigm fails
    tags.append(("msd", "unknown"))
    variables = eval_multiple_entries(p, ["apa", "bepa", "new"], tags=tags)
    assert set() == variables
