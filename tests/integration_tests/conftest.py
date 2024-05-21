import json
from pathlib import Path

import pytest


@pytest.fixture()
def test_tables() -> list[dict[str, list[str]]]:
    with Path("tests/testdata.json").open() as fp:
        return json.load(fp)
