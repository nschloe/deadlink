import pathlib

import deadlink


def test_cli():
    this_dir = pathlib.Path(__file__).resolve().parent
    files = str((this_dir / ".." / "README.md").resolve())
    deadlink.cli(["check", files, "-a", "http", "-i", "xyz"])
