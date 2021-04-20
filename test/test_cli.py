import pathlib

import urlchk


def test_cli():
    this_dir = pathlib.Path(__file__).resolve().parent
    files = str((this_dir / ".." / "README.md").resolve())
    urlchk._cli.main([files])
