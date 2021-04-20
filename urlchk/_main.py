from pathlib import Path
import requests
import re


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

    print(f"Found {len(matches)} URLs...")
    for match in matches:
        ret = requests.get(match)
        if ret.status_code != 200:
            print(f"{match} NOT OK {ret.status_code}")
    return
