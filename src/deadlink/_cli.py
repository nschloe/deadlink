import argparse
from sys import version_info

from ._check import check
from ._replace_redirects import replace_redirects


def get_version_text(prog):
    try:
        from importlib import metadata
    except ImportError:
        # Python 3.7 and earlier
        version = "unknown"
    else:
        try:
            version = metadata.version("deadlink")
        except Exception:
            version = "unknown"

    copyright = "Copyright (c) 2021 Nico Schlömer <nico.schloemer@gmail.com>"
    python_version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    return "\n".join([f"{prog} {version} [Python {python_version}]", copyright])


def cli(argv=None):
    parser = argparse.ArgumentParser(
        description="Find or replace dead links in text files."
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=get_version_text(parser.prog),
        help="display version information",
    )

    subparsers = parser.add_subparsers(title="subcommands", required=True)

    subparser_check = subparsers.add_parser(
        "check", help="Check for dead links", aliases=["c"]
    )
    _cli_check(subparser_check)
    subparser_check.set_defaults(func=check)

    subparser_rr = subparsers.add_parser(
        "replace-redirects", help="Replaces permanent redirects", aliases=["rr"]
    )
    _cli_replace_redirects(subparser_rr)
    subparser_rr.set_defaults(func=replace_redirects)

    args = parser.parse_args(argv)
    return args.func(args)


def _cli_check(parser):
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
        "-a",
        "--allow-urls",
        type=str,
        nargs="+",
        help="only consider URLs containing these strings (e.g., http:)",
    )
    parser.add_argument(
        "-i",
        "--ignore-urls",
        type=str,
        nargs="+",
        help="ignore URLs containing these strings (e.g., github.com)",
    )
    parser.add_argument(
        "-af",
        "--allow-files",
        type=str,
        nargs="+",
        help="only consider file names containing these strings (e.g., .txt)",
    )
    parser.add_argument(
        "-if",
        "--ignore-files",
        type=str,
        nargs="+",
        help="ignore file names containing these strings (e.g., .svg)",
    )


def _cli_replace_redirects(parser):
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
        "--ignore-urls",
        type=str,
        nargs="+",
        help="ignore URLs containing these strings (e.g., github.com)",
    )
    parser.add_argument(
        "-a",
        "--allow-urls",
        type=str,
        nargs="+",
        help="only consider URLs containing these strings (e.g., http:)",
    )
    parser.add_argument(
        "-af",
        "--allow-files",
        type=str,
        nargs="+",
        help="only consider file names containing these strings (e.g., .txt)",
    )
    parser.add_argument(
        "-if",
        "--ignore-files",
        type=str,
        nargs="+",
        help="ignore file names containing these strings (e.g., .svg)",
    )
    parser.add_argument(
        "-y",
        "--yes",
        default=False,
        action="store_true",
        help="automatic yes to prompt; useful for non-interactive runs (default: false)",
    )
