from regexmatcher import mregex


def test_match():
    m = mregex('(.+)a(.+)as')
    result = m.findall('bananas')
    assert [('b', 'nan'), ('ban', 'n')] == result


def test_no_match():
    m = mregex('(.+)a(.+)as')
    result = m.findall('soffa')
    assert None is result
