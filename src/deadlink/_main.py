from __future__ import annotations

import asyncio
import re
import ssl
from collections import namedtuple
from pathlib import Path
from typing import Callable
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
    url: str,
    client,
    timeout: float,
    follow_codes: list[int],
    max_num_redirects: int = 10,
    is_allowed: Callable | None = None,
):
    k = 0
    seq = []
    while True:
        if is_allowed is not None and not is_allowed(url):
            seq.append(Info(None, url))
            break

        # Pretend to be a browser <https://stackoverflow.com/a/31597823/353337>.
        # If we don't do this, sometimes we'll get a 403 where browsers don't (e.g.,
        # JSTOR).
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
        }

        try:
            r = await client.head(
                url, follow_redirects=False, timeout=timeout, headers=headers
            )
        except httpx.TimeoutException:
            seq.append(Info(901, url))
            break
        except httpx.HTTPError:
            seq.append(Info(902, url))
            break
        except ssl.SSLCertVerificationError:
            seq.append(Info(903, url))
            break
        except Exception:
            # Intercept all other errors
            seq.append(Info(900, url))
            break

        seq.append(Info(r.status_code, url))

        if (
            k >= max_num_redirects
            or r.status_code not in follow_codes
            or "Location" not in r.headers
        ):
            break

        # Handle redirect
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
    urls,
    timeout: float,
    max_connections: int,
    max_keepalive_connections: int,
    follow_codes: list[int],
    is_allowed: Callable | None = None,
):
    # return await asyncio.gather(*map(_get_return_code, urls))
    ret = []
    limits = httpx.Limits(
        max_keepalive_connections=max_keepalive_connections,
        max_connections=max_connections,
    )
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = map(
            lambda x: _get_return_code(
                x, client, timeout, follow_codes=follow_codes, is_allowed=is_allowed
            ),
            urls,
        )
        for task in track(
            asyncio.as_completed(tasks), description="Checking...", total=len(urls)
        ):
            ret.append(await task)

    return ret


def find_non_hidden_files(root):
    root = Path(root)
    if root.is_file():
        if not root.name.startswith("."):
            yield str(root)
    else:
        for path in root.glob("*"):
            if not path.name.startswith("."):
                if path.is_file():
                    yield str(path)
                else:
                    yield from find_non_hidden_files(path)


def find_files(paths: list[str]):
    return [filepath for path in paths for filepath in find_non_hidden_files(path)]


def find_urls(files):
    return set(url for f in files for url in _get_urls_from_file(f))


def replace_in_string(content: str, replacements: dict[str, str]):
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


def replace_in_file(p, redirects: dict[str, str]):
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


def read_config():
    # check if there is a config file with more allowed/ignored domains
    config_file = Path(appdirs.user_config_dir()) / "deadlink" / "config.toml"
    try:
        with open(config_file) as f:
            out = toml.load(f)
    except FileNotFoundError:
        out = {}

    return out


def is_allowed(item, allow_set: set[str], ignore_set: set[str]) -> bool:
    is_allowed = True

    if is_allowed:
        for a in allow_set:
            if re.search(a, item) is None:
                is_allowed = False
                break

    if is_allowed:
        for i in ignore_set:
            if re.search(i, item) is not None:
                is_allowed = False
                break

    return is_allowed


def categorize_urls(
    urls: set[str],
    timeout: float = 10.0,
    max_connections: int = 100,
    max_keepalive_connections: int = 10,
    is_allowed: Callable | None = None,
):
    # only follow permanent redirects
    follow_codes = [
        301,  # Moved Permanently
        308,  # Permanent Redirect
    ]
    r = asyncio.run(
        _get_all_return_codes(
            urls,
            timeout,
            max_connections,
            max_keepalive_connections,
            follow_codes,
            is_allowed,
        )
    )

    # sort results into dictionary
    d = {
        "OK": [],
        "Successful permanent redirects": [],
        "Failing permanent redirects": [],
        "Non-permanent redirects": [],
        "Client errors": [],
        "Server errors": [],
        "Timeouts": [],
        "Other errors": [],
        "Other HTTP errors": [],
        "SSL certificate errors": [],
        "Ignored": [],
    }
    for item in r:
        status_code = item[0].status_code
        if status_code is None:
            d["Ignored"].append(item)
        elif 200 <= status_code < 300:
            d["OK"].append(item)
        elif 300 <= status_code < 400:
            if status_code in [301, 308]:
                if 200 <= item[-1].status_code < 400:
                    d["Successful permanent redirects"].append(item)
                else:
                    d["Failing permanent redirects"].append(item)
            else:
                d["Non-permanent redirects"].append(item)
        elif 400 <= status_code < 500:
            d["Client errors"].append(item)
        elif 500 <= status_code < 600:
            d["Server errors"].append(item)
        elif status_code == 900:
            d["Other errors"].append(item)
        elif status_code == 901:
            d["Timeouts"].append(item)
        elif status_code == 902:
            d["Other HTTP errors"].append(item)
        elif status_code == 903:
            d["SSL certificate errors"].append(item)
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
        console.print(f"{key} ({num})", style="green", highlight=False)

    key = "Non-permanent redirects"
    if key in d and len(d[key]) > 0:
        print()
        num = len(d[key])
        console.print(f"{key} ({num})", style="green", highlight=False)

    key = "Ignored"
    if key in d and len(d[key]) > 0:
        print()
        num = len(d[key])
        console.print(f"{key} ({num})", style="white", highlight=False)

    keycol = [
        ("Successful permanent redirects", "yellow"),
        ("Failing permanent redirects", "red"),
    ]
    for key, base_color in keycol:
        if key not in d or len(d[key]) == 0:
            continue
        print()
        console.print(f"{key} ({len(d[key])}):", style=base_color, highlight=False)
        for seq in d[key]:
            for k, item in enumerate(seq):
                if item.status_code < 300:
                    color = "green"
                elif (300 <= item.status_code < 400) or item.status_code is None:
                    color = "yellow"
                else:
                    color = "red"

                sc = "xxx" if item.status_code is None else item.status_code
                if k == 0:
                    console.print(f"   [dim]{sc}[/]:   {item.url}", style=color)
                else:
                    console.print(f"   → [dim]{sc}[/]: {item.url}", style=color)

    for key in [
        "Client errors",
        "Server errors",
        "Timeouts",
        "Other errors",
        "Other HTTP errors",
        "SSL certificate errors",
    ]:
        if key not in d or len(d[key]) == 0:
            continue
        print()
        console.print(f"{key} ({len(d[key])}):", style="red", highlight=False)
        for item in d[key]:
            url = item[0].url
            status_code = item[0].status_code
            if item[0].status_code < 900:
                console.print(f"  [dim]{status_code}[/]: {url}", style="red")
            else:
                console.print(f"  {url}", style="red")


def plural(number: int, noun: str) -> str:
    out = str(number) + " " + noun
    if number != 1:
        out += "s"
    return out
