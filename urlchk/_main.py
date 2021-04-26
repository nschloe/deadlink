import asyncio
import re
from pathlib import Path
from typing import Optional, Set
from urllib.parse import urlparse

import appdirs
import httpx
import toml
from rich.console import Console
from rich.progress import track

# https://regexr.com/3e6m0
# make all groups non-capturing with ?:
pattern = re.compile(
    r"http(?:s)?:\/\/.(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b(?:[-a-zA-Z0-9@:%_\+.~#?&/=]*)"
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
        httpx.PoolTimeout,
    ):
        return url, 999, None
    else:
        loc = r.headers["Location"] if "Location" in r.headers else None
        return url, r.status_code, loc


async def _get_all_return_codes(
    urls, timeout, max_connections, max_keepalive_connections
):
    # return await asyncio.gather(*map(_get_return_code, urls))
    ret = []
    limits = httpx.Limits(
        max_keepalive_connections=max_keepalive_connections,
        max_connections=max_connections,
    )
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = map(lambda x: _get_return_code(x, client, timeout), urls)
        for task in track(
            asyncio.as_completed(tasks), description="Checking...", total=len(urls)
        ):
            ret.append(await task)
    return ret


def check_paths(
    paths,
    timeout: float = 10.0,
    max_connections: int = 100,
    max_keepalive_connections: int = 10,
    ignore_domains: Optional[Set[str]] = None,
):
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

    # remove duplicate
    urls = set(urls)
    print(f"Found {len(urls)} unique HTTP URLs")
    d = check_urls(
        urls, timeout, max_connections, max_keepalive_connections, ignore_domains
    )
    print_to_screen(d)
    has_errors = any(
        len(d[key]) > 0
        for key in ["Client errors", "Server errors", "Timeouts", "Other errors"]
    )
    return has_errors


def _filter_ignored(urls, ignore_domains):
    # check if there is a config file with more ignored domains
    config_file = Path(appdirs.user_config_dir()) / "urlchk" / "config.toml"
    try:
        with open(config_file) as f:
            out = toml.load(f)
    except FileNotFoundError:
        pass
    else:
        ignore_domains = ignore_domains.union(set(out["ignore"]))

    # filter out the ignored urls
    ignored_urls = set()
    filtered_urls = set()
    for url in urls:
        parsed_uri = urlparse(url)
        if parsed_uri.netloc in ignore_domains:
            ignored_urls.add(url)
        else:
            filtered_urls.add(url)
    urls = filtered_urls
    return urls, ignored_urls


def check_urls(
    urls: Set[str],
    timeout: float = 10.0,
    max_connections: int = 100,
    max_keepalive_connections: int = 10,
    ignore_domains: Optional[Set[str]] = None,
):
    if ignore_domains is None:
        ignore_domains = set()

    urls, ignored_urls = _filter_ignored(urls, ignore_domains)

    r = asyncio.run(
        _get_all_return_codes(urls, timeout, max_connections, max_keepalive_connections)
    )
    # sort results into dictionary
    d = {
        "OK": [],
        "Ignored": ignored_urls,
        "Redirects": [],
        "Client errors": [],
        "Server errors": [],
        "Timeouts": [],
        "Other errors": [],
    }
    for item in r:
        status_code = item[1]
        if 200 <= status_code < 300:
            d["OK"].append(item)
        elif 300 <= status_code < 400:
            d["Redirects"].append(item)
        elif 400 <= status_code < 500:
            d["Client errors"].append(item)
        elif 500 <= status_code < 600:
            d["Server errors"].append(item)
        elif status_code == 998:
            d["Timeouts"].append(item)
        elif status_code == 999:
            d["Other errors"].append(item)
        else:
            raise RuntimeError(f"Unknown status code {status_code}")

    return d


def print_to_screen(d):
    # sort by status code
    for key, value in d.items():
        d[key] = sorted(value, key=lambda x: x[1])

    console = Console()

    if len(d["OK"]) > 0:
        print()
        console.print(f"OK ({len(d['OK'])})", style="green")

    if len(d["Ignored"]) > 0:
        print()
        console.print(f"Ignored ({len(d['Ignored'])})", style="white")

    if len(d["Redirects"]) > 0:
        print()
        console.print(f"Redirects ({len(d['Redirects'])}):", style="yellow")
        for url, status_code, loc in d["Redirects"]:
            console.print(f"  {status_code}: {url}", style="yellow")
            console.print(f"     → {loc}", style="yellow")

    for key in ["Client errors", "Server errors", "Timeouts", "Other errors"]:
        err = d[key]
        if len(err) > 0:
            print()
            console.print(f"{key} ({len(err)}):", style="red")
            for url, status_code, _ in err:
                if status_code < 900:
                    console.print(f"  {status_code}: {url}", style="red")
                else:
                    console.print(f"  {url}", style="red")
