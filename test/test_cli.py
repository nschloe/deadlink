import pathlib

import wurl


def test_cli():
    this_dir = pathlib.Path(__file__).resolve().parent
    files = str((this_dir / ".." / "README.md").resolve())
    wurl._cli.check([files])
