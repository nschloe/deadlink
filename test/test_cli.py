import pathlib

import urli


def test_cli():
    this_dir = pathlib.Path(__file__).resolve().parent
    files = str((this_dir / ".." / "README.md").resolve())
    urli._cli.check([files])
