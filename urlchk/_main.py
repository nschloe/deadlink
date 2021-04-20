import asyncio
import re
from pathlib import Path

import httpx
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


async def _get_return_code(url: str, client, timeout: float):
    try:
        r = await client.head(url, allow_redirects=False, timeout=timeout)
    except httpx.ConnectTimeout:
        return url, 998, None
    except (
        httpx.RemoteProtocolError,
        httpx.ReadTimeout,
        httpx.LocalProtocolError,
        httpx.ConnectError,
        httpx.ReadError,
    ):
        return url, 999, None
    else:
        loc = r.headers["Location"] if "Location" in r.headers else None
        return url, r.status_code, loc


async def _get_all_return_codes(urls, timeout):
    # return await asyncio.gather(*map(_get_return_code, urls))
    ret = []
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=100)
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = map(lambda x: _get_return_code(x, client, timeout), urls)
        for task in track(
            asyncio.as_completed(tasks), description="Checking...", total=len(urls)
        ):
            ret.append(await task)
    return ret


def check(paths, timeout):
    urls = []
    for path in paths:
        path = Path(path)
        if path.is_dir():
            for p in path.rglob("*"):
                if p.is_file():
                    urls += _get_urls_from_file(p)
        elif path.is_file():
            urls += _get_urls_from_file(path)
        else:
            raise ValueError(f"Could not find path {path}")

    # remove duplicated
    urls = set(urls)

    print(f"Found {len(urls)} unique HTTP URLs")
    r = asyncio.run(_get_all_return_codes(urls, timeout))
    not_ok = [item for item in r if item[1] != 200]

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
    timeout_errors = [
        (url, status_code, loc)
        for url, status_code, loc in not_ok
        if status_code == 998
    ]
    other_errors = [
        (url, status_code, loc)
        for url, status_code, loc in not_ok
        if status_code == 999
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
        console.print("Server errors:", style="red")
        for url, status_code, _ in server_errors:
            console.print(f"  {status_code}: {url}", style="red")

    if len(timeout_errors) > 0:
        print()
        console.print("Timeouts:", style="red")
        for url, status_code, _ in timeout_errors:
            console.print(f"  {url}", style="red")

    if len(other_errors) > 0:
        print()
        console.print("Other errors:", style="red")
        for url, status_code, _ in other_errors:
            console.print(f"  {url}", style="red")

    return len(client_errors) > 0 or len(server_errors) > 0
