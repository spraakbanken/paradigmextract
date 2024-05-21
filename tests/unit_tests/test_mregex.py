from paradigmextract.regexmatcher import MRegex


def test_match():
    m = MRegex("(.+)a(.+)as")
    result = m.findall("bananas")
    assert result == [("b", "nan"), ("ban", "n")]


def test_no_match():
    m = MRegex("(.+)a(.+)as")
    result = m.findall("soffa")
    assert None is result
