import random
from pathlib import Path

from ._main import (
    categorize_urls,
    find_files,
    find_urls,
    is_allowed,
    plural,
    print_to_screen,
    read_config,
    replace_in_file,
)


def replace_redirects(args):
    # get non-hidden files in non-hidden directories
    files = find_files(args.paths)

    d = read_config()

    # filter files by allow-ignore-lists
    allow_patterns = set() if args.allow_files is None else set(args.allow_files)
    if "allow_files" in d:
        allow_patterns = allow_patterns.union(set(d["allow_files"]))
    ignore_patterns = set() if args.ignore_files is None else set(args.ignore_files)
    if "ignore_files" in d:
        ignore_patterns = ignore_patterns.union(set(d["ignore_files"]))

    num_files_before = len(files)
    files = set(
        filter(lambda item: is_allowed(item, allow_patterns, ignore_patterns), files)
    )
    num_ignored_files = num_files_before - len(files)

    allow_patterns = set() if args.allow_urls is None else set(args.allow_urls)
    if "allow_urls" in d:
        allow_patterns = allow_patterns.union(set(d["allow_urls"]))
    ignore_patterns = set() if args.ignore_urls is None else set(args.ignore_urls)
    if "ignore_urls" in d:
        ignore_patterns = ignore_patterns.union(set(d["ignore_urls"]))

    urls = find_urls(files)

    # Shuffle the urls. In case there's rate limiting (e.g., on github.com),
    # different URLs are checked on every turn.
    urls = list(urls)
    random.shuffle(urls)

    urls_str = plural(len(urls), "unique URL")
    files_str = plural(len(files), "file")
    ifiles_str = plural(num_ignored_files, "file")
    print(f"Found {urls_str} in {files_str} (ignored {ifiles_str})")

    d = categorize_urls(
        urls,
        args.timeout,
        args.max_connections,
        args.max_keepalive_connections,
        lambda url: is_allowed(url, allow_patterns, ignore_patterns),
    )

    # only consider successful permanent redirects
    redirects = d["Successful permanent redirects"]

    if len(redirects) == 0:
        print("No redirects found.")
        return 0

    print_to_screen({"Successful permanent redirects": redirects})
    rdr = "redirect" if len(redirects) == 1 else "redirects"
    print(f"\nReplace those {len(redirects)} {rdr}? [y/N] ", end="")

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
        else:
            assert path.is_file()
            replace_in_file(path, replace)

    return 0
