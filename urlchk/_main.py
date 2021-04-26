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
    return check_urls(
        urls, timeout, max_connections, max_keepalive_connections, ignore_domains
    )


def check_urls(
    urls: Set[str],
    timeout: float = 10.0,
    max_connections: int = 100,
    max_keepalive_connections: int = 10,
    ignore_domains: Optional[Set[str]] = None,
):
    if ignore_domains is None:
        ignore_domains = set()

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

    r = asyncio.run(
        _get_all_return_codes(urls, timeout, max_connections, max_keepalive_connections)
    )
    num_ok = len([item for item in r if item[1] == 200])
    not_ok = [item for item in r if item[1] != 200]

    # sort by status code
    not_ok.sort(key=lambda x: x[1])

    redirects = []
    errors = {
        "Client errors": [],
        "Server errors": [],
        "Timeouts": [],
        "Other errors": [],
    }
    for item in not_ok:
        status_code = item[1]
        if 300 <= status_code < 400:
            redirects.append(item)
        elif 400 <= status_code < 500:
            errors["Client errors"].append(item)
        elif 500 <= status_code < 600:
            errors["Server errors"].append(item)
        elif status_code == 998:
            errors["Timeouts"].append(item)
        elif status_code == 999:
            errors["Other errors"].append(item)
        else:
            raise RuntimeError(f"Unknown status code {status_code}")

    console = Console()

    if num_ok > 0:
        print()
        console.print(f"OK ({num_ok})", style="green")

    if len(ignored_urls) > 0:
        print()
        console.print(f"Ignored ({len(ignored_urls)})", style="white")

    if len(redirects) > 0:
        print()
        console.print(f"Redirects ({len(redirects)}):", style="yellow")
        for url, status_code, loc in redirects:
            console.print(f"  {status_code}: {url}", style="yellow")
            console.print(f"     → {loc}", style="yellow")

    for key, err in errors.items():
        if len(err) > 0:
            print()
            console.print(f"{key} ({len(err)}):", style="red")
            for url, status_code, _ in err:
                if status_code < 900:
                    console.print(f"  {status_code}: {url}", style="red")
                else:
                    console.print(f"  {url}", style="red")

    return any(len(err) > 0 for err in errors.values())
