import re
from pathlib import Path

import requests
from rich.console import Console
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
        r = requests.head(match, allow_redirects=False)
        if "Location" in r.headers:
            not_ok.append((match, r.status_code, r.headers["Location"]))
        elif r.status_code != 200:
            not_ok.append((match, r.status_code, None))

    # sort by status code
    not_ok.sort(key=lambda x: x[1])

    redirects = [
        (url, status_code, loc)
        for url, status_code, loc in not_ok
        if status_code >= 300 and status_code < 400
    ]
    client_errors = [
        (url, status_code, loc)
        for url, status_code, loc in not_ok
        if status_code >= 400 and status_code < 500
    ]
    server_errors = [
        (url, status_code, loc)
        for url, status_code, loc in not_ok
        if status_code >= 500 and status_code < 600
    ]

    console = Console()

    if len(redirects) > 0:
        print()
        console.print("Redirects:", style="yellow")
        for url, status_code, loc in redirects:
            console.print(f"  {status_code}: {url}", style="yellow")
            console.print(f"     → {loc}", style="yellow")

    if len(client_errors) > 0:
        print()
        console.print("Client errors:", style="red")
        for url, status_code, _ in client_errors:
            console.print(f"  {status_code}: {url}", style="red")

    if len(server_errors) > 0:
        print()
        console.print("Server errors:")
        for url, status_code, _ in server_errors:
            console.print(f"  {status_code}: {url}", style="red")
