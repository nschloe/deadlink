import re
from pathlib import Path

import requests
from rich.progress import track

# https://regexr.com/3e6m0
# make all groups non-capturing with ?:
pattern = re.compile(
    r"http(?:s)?:\/\/.(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)"
)


def _get_urls_from_file(path):
    try:
        with open(path) as f:
            content = f.read()
    except UnicodeDecodeError:
        return []
    return pattern.findall(content)


def check(path):
    path = Path(path)

    matches = []
    if path.is_dir():
        for p in path.rglob("*"):
            if p.is_file():
                matches += _get_urls_from_file(p)
    elif not path.is_file():
        matches += _get_urls_from_file(path)
    else:
        raise ValueError(f"Could not find path {path}.")

    print(f"Found {len(matches)} URLs")
    not_ok = []
    for match in track(matches, description="Checking..."):
        ret = requests.get(match, allow_redirects=False)
        if ret.status_code != 200:
            not_ok.append((match, ret.status_code))

    for url, status_code in not_ok:
        print(f"NOT OK ({status_code}): {url}")
