import tempfile
from pathlib import Path

import pytest

import deadlink


def test_replace():
    content = (
        "some text\n"
        + "http://example.com\n"
        + "http://example.com/path\n"
        + "more text"
    )
    d = {
        "http://example.com/path": "http://example.com/path/more",
        "http://example.com": "http://example.com/home",
    }
    new_content = deadlink._main.replace_in_string(content, d)

    ref = (
        "some text\n"
        + "http://example.com/home\n"
        + "http://example.com/path/more\n"
        + "more text"
    )
    assert ref == new_content


@pytest.mark.parametrize(
    "content, ref",
    [
        (
            "some text\nhttps://httpstat.us/301\nmore text",
            "some text\nhttps://httpstat.us\nmore text",
        ),
        # For some reason, http://www.google.com doesn't get redirected
        # https://stackoverflow.com/q/68303464/353337
        # (
        #     "http://www.google.com",
        #     "https://www.google.com"
        # )
    ],
)
def test_fix_cli(content, ref):

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        infile = tmpdir / "in.txt"
        with open(infile, "w") as f:
            f.write(content)

        deadlink.cli(["replace-redirects", str(infile), "--yes"])

        with open(infile) as f:
            out = f.read()

        assert out == ref
