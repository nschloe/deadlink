import argparse
import sys

from ..__about__ import __version__
from .._main import categorize_urls, filter_urls, find_urls, print_to_screen


def check(argv=None):
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

    print_to_screen(d)
    has_errors = any(
        len(d[key]) > 0
        for key in ["Client errors", "Server errors", "Timeouts", "Other errors"]
    )
    return 1 if has_errors else 0


def _get_parser():
    parser = argparse.ArgumentParser(
        description=("Check URLs in text files."),
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
