import asyncio
import re
from collections import namedtuple
from pathlib import Path
from typing import Dict, Optional, Set
from urllib.parse import urlsplit, urlunsplit

import appdirs
import httpx
import toml
from rich.console import Console
from rich.progress import track

# https://regexr.com/3e6m0
# make all groups non-capturing with ?:
url_regex = re.compile(
    r"http(?:s)?:\/\/.(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b(?:[-a-zA-Z0-9@:%_\+.~#?&/=]*)"
)

Info = namedtuple("Info", ["status_code", "url"])


def _get_urls_from_file(path):
    try:
        with open(path) as f:
            content = f.read()
    except UnicodeDecodeError:
        return []
    return url_regex.findall(content)


async def _get_return_code(
    url: str, client, timeout: float, max_num_redirects: int = 10
):
    k = 0
    seq = []
    while True:
        if k >= max_num_redirects:
            seq.append(Info(997, url))
            break

        try:
            r = await client.head(url, allow_redirects=False, timeout=timeout)
        except httpx.ConnectTimeout:
            seq.append(Info(998, url))
            break
        except (
            httpx.RemoteProtocolError,
            httpx.ReadTimeout,
            httpx.LocalProtocolError,
            httpx.ConnectError,
            httpx.ReadError,
            httpx.PoolTimeout,
        ):
            seq.append(Info(999, url))
            break

        seq.append(Info(r.status_code, url))

        if "Location" not in r.headers:
            break

        # Handle redirect
        assert 300 <= r.status_code < 400
        loc = r.headers["Location"]
        url_split = urlsplit(url)

        # create loc split that can be overridden
        loc_split = urlsplit(loc)
        loc_split = [
            loc_split.scheme,
            loc_split.netloc,
            loc_split.path,
            loc_split.query,
            loc_split.fragment,
        ]

        # handle relative redirects
        if loc_split[0] == "":
            loc_split[0] = url_split.scheme
        if loc_split[1] == "":
            loc_split[1] = url_split.netloc

        # The URL fragment, if (the part after a #-sign, if there is one) is not
        # contained in the redirect location because it's not sent to the server in the
        # first place.  Append it manually.
        if url_split.fragment != "" and loc_split[4] == "":
            loc_split[4] = url_split.fragment

        url = urlunsplit(loc_split)

        k += 1

    return seq


async def _get_all_return_codes(
    urls, timeout: float, max_connections: int, max_keepalive_connections: int
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


def find_urls(paths):
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
    return set(urls)


def replace_in_string(content: str, replacements: Dict[str, str]):
    # register where to replace what
    repl = [
        (m.span(0), replacements[m.group(0)])
        for m in url_regex.finditer(content)
        if m.group(0) in replacements
    ]

    k0 = 0
    out = []
    for k in range(len(repl)):
        span, string = repl[k]
        out.append(content[k0 : span[0]])
        out.append(string)
        k0 = span[1]
    # and the rest
    out.append(content[k0:])
    return "".join(out)


def replace_in_file(p, redirects: Dict[str, str]):
    # read
    try:
        with open(p) as f:
            content = f.read()
    except UnicodeDecodeError:
        return
    # replace
    new_content = replace_in_string(content, redirects)
    # rewrite
    if new_content != content:
        with open(p, "w") as f:
            f.write(new_content)


def filter_urls(
    urls: Set[str], allow_set: Optional[Set[str]], ignore_set: Optional[Set[str]]
):
    if allow_set is None:
        allow_set = set()
    if ignore_set is None:
        ignore_set = set()

    # check if there is a config file with more allowed/ignored domains
    config_file = Path(appdirs.user_config_dir()) / "deadlink" / "config.toml"
    try:
        with open(config_file) as f:
            out = toml.load(f)
    except FileNotFoundError:
        pass
    else:
        if "allow" in out:
            allow_set = allow_set.union(set(out["allow"]))
        if "ignore" in out:
            ignore_set = ignore_set.union(set(out["ignore"]))

    # filter out non-allowed and ignored urls
    allowed_urls = set()
    ignored_urls = set()
    for url in urls:
        is_allowed = True

        if is_allowed:
            for a in allow_set:
                if re.search(a, url) is None:
                    is_allowed = False
                    break

        if is_allowed:
            for i in ignore_set:
                if re.search(i, url) is not None:
                    is_allowed = False
                    break

        if is_allowed:
            allowed_urls.add(url)
        else:
            ignored_urls.add(url)

    return allowed_urls, ignored_urls


def categorize_urls(
    urls: Set[str],
    timeout: float = 10.0,
    max_connections: int = 100,
    max_keepalive_connections: int = 10,
):
    r = asyncio.run(
        _get_all_return_codes(urls, timeout, max_connections, max_keepalive_connections)
    )

    # sort results into dictionary
    d = {
        "OK": [],
        "Successful redirects": [],
        "Failing redirects": [],
        "Client errors": [],
        "Server errors": [],
        "Timeouts": [],
        "Other errors": [],
    }
    for item in r:
        status_code = item[0].status_code
        if 200 <= status_code < 300:
            d["OK"].append(item)
        elif 300 <= status_code < 400:
            if 200 <= item[-1].status_code < 300:
                d["Successful redirects"].append(item)
            else:
                d["Failing redirects"].append(item)
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
        d[key] = sorted(value, key=lambda x: x[0].status_code)

    console = Console()

    key = "OK"
    if key in d and len(d[key]) > 0:
        print()
        num = len(d[key])
        console.print(f"{key} ({num})", style="green")

    key = "Ignored"
    if key in d and len(d[key]) > 0:
        print()
        num = len(d[key])
        console.print(f"{key} ({num})", style="white")

    keycol = [("Successful redirects", "yellow"), ("Failing redirects", "red")]
    for key, base_color in keycol:
        if key not in d or len(d[key]) == 0:
            continue
        print()
        console.print(f"{key} ({len(d[key])}):", style=base_color)
        for seq in d[key]:
            for k, item in enumerate(seq):
                if item.status_code < 300:
                    color = "green"
                elif 300 <= item.status_code < 400:
                    color = "yellow"
                else:
                    color = "red"
                if k == 0:
                    console.print(f"   {item.status_code}:   {item.url}", style=color)
                else:
                    console.print(f"   → {item.status_code}: {item.url}", style=color)

    for key in ["Client errors", "Server errors", "Timeouts", "Other errors"]:
        if key not in d or len(d[key]) == 0:
            continue
        print()
        console.print(f"{key} ({len(d[key])}):", style="red")
        for item in d[key]:
            url = item[0].url
            status_code = item[0].status_code
            if item[0].status_code < 900:
                console.print(f"  {status_code}: {url}", style="red")
            else:
                console.print(f"  {url}", style="red")
