from paradigmextract.paradigm import Form


def test_constructor_minimum():
    form = Form("")

    assert form.form == [""]
    # assert isinstance(form.msd, list)


def test_constructor_single_msd():
    msd = [("vb",)]
    form = Form("", msd)

    assert form.msd == [("vb",)]
