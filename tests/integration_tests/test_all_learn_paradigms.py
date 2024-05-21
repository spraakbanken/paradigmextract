import json
from pathlib import Path

from paradigmextract.pextract import learnparadigms


def test_all():
    with Path("tests/testdata.json").open() as fp:
        test_tables = json.load(fp)
    final_tables = []
    assert len(test_tables) == 9943
    for table in test_tables:
        msds_ = table["msds"]
        tags = [("msd", msd) for msd in msds_]
        final_tables.append((table["wordforms"], tags))
    new_paradigms = learnparadigms(final_tables)
    # this value is transient, sometimes 551 sometimes 552 (for full testset)
    # it differs for the words "bortgallra", "bortkollra", "bortjaga", "bortsopa"
    # where they sometimes are all in the same paradigm and sometimes "bortjaga" is its own paradigm
    assert len(new_paradigms) in {551, 552}
