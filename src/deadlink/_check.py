from ._main import (
    categorize_urls,
    find_files,
    find_urls,
    is_allowed,
    print_to_screen,
    read_config,
)


def check(args):
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

    num_urls_before = len(urls)
    urls = set(
        filter(lambda item: is_allowed(item, allow_patterns, ignore_patterns), urls)
    )
    num_ignored_urls = num_urls_before - len(urls)

    print(
        f"Found {len(urls)} unique URLs in {len(files)} files "
        f"(ignored {num_ignored_files} files, {num_ignored_urls} URLs)"
    )
    d = categorize_urls(
        urls,
        args.timeout,
        args.max_connections,
        args.max_keepalive_connections,
    )

    print_to_screen(d)
    has_errors = any(
        len(d[key]) > 0
        for key in ["Client errors", "Server errors", "Timeouts", "Other errors"]
    )
    return 1 if has_errors else 0
