import sys

from .__about__ import __version__
from ._main import check


def main(argv=None):
    # Parse command line arguments.
    parser = _get_parser()
    args = parser.parse_args(argv)

    check(args.path)


def _get_parser():
    import argparse

    parser = argparse.ArgumentParser(
        description=("Check URLs in text files."),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("path", type=str, help="file or path to check")

    __copyright__ = "Copyright (c) 2021 Nico Schlömer <nico.schloemer@gmail.com>"
    version_text = "\n".join(
        [
            "urlchk {} [Python {}.{}.{}]".format(
                __version__,
                sys.version_info.major,
                sys.version_info.minor,
                sys.version_info.micro,
            ),
            __copyright__,
        ]
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=version_text,
        help="display version information",
    )

    return parser
