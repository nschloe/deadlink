import re
from pathlib import Path

import requests
from rich.progress import track


def check(path):
    path = Path(path)

    # https://regexr.com/3e6m0
    # make all groups non-capturing with ?:
    pattern = re.compile(
        r"http(?:s)?:\/\/.(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)"
    )

    matches = []
    if path.is_file():
        with open(path) as f:
            fread = f.read()
            matches += pattern.findall(fread)

    print(f"Found {len(matches)} URLs")
    not_ok = []
    for match in track(matches, description="Checking..."):
        ret = requests.get(match)
        if ret.status_code != 200:
            not_ok.append((match, ret.status_code))

    for url, status_code in not_ok:
        print(f"NOT OK ({status_code}): {url}")
