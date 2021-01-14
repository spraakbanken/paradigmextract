from paradigmextract import morphparser, paradigm


def test_eval_baseform_fightas():
    para = paradigm.Paradigm(
        form_msds=[
            ("1+2", "pres ind s-form"),
            ("1+de+2", "pret ind s-form"),
            ("1+2", "imper"),
            ("1+2", "inf s-form"),
            ("1+t+2", "sup s-form"),
        ],
        var_insts=[[("1", "anda"), ("2", "s")]],
    )
    variables = morphparser.eval_baseform(para, "fightas", ("inf aktiv", "inf s-form"))

    assert variables == ["fighta", "s"]


def test_eval_baseform_av_1():
    para = paradigm.Paradigm(
        form_msds=[
            ("1", "pos indef sg u nom"),
        ],
        var_insts=[[("1", "blå")]],
    )
    variables = morphparser.eval_baseform(para, "grå")

    assert variables == ["grå"]


def test_eval_baseform_nn_1():
    para = paradigm.Paradigm(
        form_msds=[("1+o+2", "sg indef nom")], var_insts=[[("1", "s"), ("2", "n")]]
    )
    variables = morphparser.eval_baseform(para, "styrelseledamot")

    assert variables == ["styrelseledam", "t"]