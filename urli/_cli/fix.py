import argparse
import sys
from pathlib import Path

from ..__about__ import __version__
from .._main import (
    _filter,
    _find_urls,
    _replace_in_file,
    categorize_urls,
    print_to_screen,
)


def fix(argv=None):
    # Parse command line arguments.
    parser = _get_parser()
    args = parser.parse_args(argv)

    urls = _find_urls(args.paths)
    urls, ignored_urls = _filter(
        urls,
        None if args.allow is None else set(args.allow),
        None if args.ignore is None else set(args.ignore),
    )

    print(f"Found {len(urls)} unique HTTP URLs (ignored {len(ignored_urls)})")
    d = categorize_urls(
        urls, args.timeout, args.max_connections, args.max_keepalive_connections
    )

    # only consider redirects
    redirects = d["Redirects"]
    if len(redirects) == 0:
        print("No redirects found.")
        return 0

    print_to_screen({"Redirects": redirects})
    print()
    print("Replace those redirects? [y/N] ", end="")
    choice = input().lower()
    if choice not in ["y", "yes"]:
        print("Abort.")
        return 1

    for path in args.paths:
        path = Path(path)
        if path.is_dir():
            for p in path.rglob("*"):
                if p.is_file():
                    _replace_in_file(p, redirects)
        elif path.is_file():
            _replace_in_file(path, redirects)
        else:
            raise ValueError(f"Could not find path {path}")

    return 0


def _get_parser():
    parser = argparse.ArgumentParser(
        description=("Fixes URLs in text files."),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("paths", type=str, nargs="+", help="files or paths to check")
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=10.0,
        help="connection timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "-c",
        "--max-connections",
        type=int,
        default=100,
        help="maximum number of allowable connections (default: 100)",
    )
    parser.add_argument(
        "-k",
        "--max-keepalive-connections",
        type=int,
        default=10,
        help="number of allowable keep-alive connections (default: 10)",
    )
    parser.add_argument(
        "-i",
        "--ignore",
        type=str,
        nargs="+",
        help="ignore URLs containing these strings (e.g., github.com)",
    )
    parser.add_argument(
        "-a",
        "--allow",
        type=str,
        nargs="+",
        help="only consider URLs containing these strings (e.g., http:)",
    )

    __copyright__ = "Copyright (c) 2021 Nico Schlömer <nico.schloemer@gmail.com>"
    version_text = "\n".join(
        [
            "urli {} [Python {}.{}.{}]".format(
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
