from morphparser import eval_multiple_entries
from paradigm import Paradigm


def test_1():
    form_msds = [('1', ('msd', 'sg indef nom')), ('1+n', ('msd', 'pl def nom')), ('1+ns', ('msd', 'sg def gen'))]
    var_insts = [[('1', 'apa')]]
    p = Paradigm(form_msds, var_insts)
    words = ['apa', 'apan', 'apans']
    variables = eval_multiple_entries(p, words, baseform=True)
    assert {('apa',)} == variables


def test_2():
    form_msds = [('apa', ('msd', 'sg indef nom')), ('bepa', ('msd', 'pl def nom'))]
    p = Paradigm(form_msds, [[]])
    words = ['apa']
    variables = eval_multiple_entries(p, words, baseform=True)
    assert {()} == variables


def test_3():
    form_msds = [('apa', ('msd', 'sg indef nom')), ('bepa', ('msd', 'pl def nom'))]
    p = Paradigm(form_msds, [[]])
    words = ['apa']
    variables = eval_multiple_entries(p, words, baseform=False)
    assert {()} == variables
