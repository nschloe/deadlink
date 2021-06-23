import argparse
import sys
from pathlib import Path

from ..__about__ import __version__
from .._main import (
    categorize_urls,
    filter_urls,
    find_urls,
    print_to_screen,
    replace_in_file,
)


def fix(argv=None):
    # Parse command line arguments.
    parser = _get_parser()
    args = parser.parse_args(argv)

    urls = find_urls(args.paths)
    urls, ignored_urls = filter_urls(
        urls,
        None if args.allow is None else set(args.allow),
        None if args.ignore is None else set(args.ignore),
    )

    print(f"Found {len(urls)} unique HTTP(s) URLs (ignored {len(ignored_urls)})")
    d = categorize_urls(
        urls, args.timeout, args.max_connections, args.max_keepalive_connections
    )

    # only consider successful redirects
    redirects = d["Successful redirects"]

    if len(redirects) == 0:
        print("No redirects found.")
        return 0

    print_to_screen({"Successful redirects": redirects})
    print()
    print("Replace those redirects? [y/N] ", end="")
    if args.yes:
        print("Auto yes.")
    else:
        choice = input().lower()
        if choice not in ["y", "yes"]:
            print("Abort.")
            return 1

    # create a dictionary from redirects
    replace = dict([(r[0].url, r[-1].url) for r in redirects])

    for path in args.paths:
        path = Path(path)
        if path.is_dir():
            for p in path.rglob("*"):
                if p.is_file():
                    replace_in_file(p, replace)
        elif path.is_file():
            replace_in_file(path, replace)
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
    parser.add_argument(
        "-y",
        "--yes",
        default=False,
        action="store_true",
        help="automatic yes to prompt; useful for non-interactive runs (default: false)",
    )

    __copyright__ = "Copyright (c) 2021 Nico Schlömer <nico.schloemer@gmail.com>"
    version_text = "\n".join(
        [
            "deadlink {} [Python {}.{}.{}]".format(
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
