<p align="center">
  <a href="https://github.com/nschloe/wurl"><img alt="wurl" src="https://nschloe.github.io/wurl/logo.svg" width="60%"></a>
  <p align="center">The wurly bird catches the worm.</p>
</p>

[![PyPi Version](https://img.shields.io/pypi/v/wurl.svg?style=flat-square)](https://pypi.org/project/wurl/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/wurl.svg?style=flat-square)](https://pypi.org/project/wurl/)
[![GitHub stars](https://img.shields.io/github/stars/nschloe/wurl.svg?style=flat-square&logo=github&label=Stars&logoColor=white)](https://github.com/nschloe/wurl/)
[![PyPi downloads](https://img.shields.io/pypi/dm/wurl.svg?style=flat-square)](https://pypistats.org/packages/wurl)

[![gh-actions](https://img.shields.io/github/workflow/status/nschloe/wurl/ci?style=flat-square)](https://github.com/nschloe/wurl/actions?query=workflow%3Aci)
[![codecov](https://img.shields.io/codecov/c/github/nschloe/wurl.svg?style=flat-square)](https://app.codecov.io/gh/nschloe/wurl)
[![LGTM](https://img.shields.io/lgtm/grade/python/github/nschloe/wurl.svg?style=flat-square)](https://lgtm.com/projects/g/nschloe/wurl)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

Parses text files for HTTP URLs and checks if they are still valid. Install with
```
pip install wurl
```
and use as
```sh
wurl-check README.md   # or multiple files/directories
```
To explicitly allow or ignore certain URLs, use
```
wurl-check README.md -a http: -i stackoverflow.com github
```
This only considers URLs containing `http:` and _not_ containing `stackoverflow.com` or
`github`. You can also place allow and ignore lists in the config file
`~/.config/wurl/config.toml`, e.g.,
```toml
allow = [
  "https:"
]
ignore = [
  "stackoverflow.com",
  "math.stackexchange.com",
  "discord.gg",
  "doi.org"
]
```
See
```
wurl-check -h
```
for all options. Use
```
wurl-fix path-or-file
```
to replace redirects in ann files. The same filters as for `wurl-check` apply.

Example output:

![](https://nschloe.github.io/wurl/example-output-carbon.png)


### License
wurl is published under the [MIT license](https://en.wikipedia.org/wiki/MIT_License).
