import tempfile
from pathlib import Path

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


def test_fix_cli():
    content = "some text\n" + "https://httpstat.us/302\n" + "more text"
    ref = "some text\n" + "https://httpstat.us\n" + "more text"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        infile = tmpdir / "in.txt"
        with open(infile, "w") as f:
            f.write(content)

        deadlink._cli.fix([str(infile), "--yes"])

        with open(infile) as f:
            out = f.read()

        assert out == ref
