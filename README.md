<p align="center">
  <a href="https://github.com/nschloe/urlchk"><img alt="urlchk" src="https://nschloe.github.io/urlchk/logo.svg" width="60%"></a>
  <p align="center">Checks URLs in text files.</p>
</p>

[![PyPi Version](https://img.shields.io/pypi/v/urlchk.svg?style=flat-square)](https://pypi.org/project/urlchk/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/urlchk.svg?style=flat-square)](https://pypi.org/project/urlchk/)
[![GitHub stars](https://img.shields.io/github/stars/nschloe/urlchk.svg?style=flat-square&logo=github&label=Stars&logoColor=white)](https://github.com/nschloe/urlchk/)
[![PyPi downloads](https://img.shields.io/pypi/dm/urlchk.svg?style=flat-square)](https://pypistats.org/packages/urlchk)

[![gh-actions](https://img.shields.io/github/workflow/status/nschloe/urlchk/ci?style=flat-square)](https://github.com/nschloe/urlchk/actions?query=workflow%3Aci)
[![codecov](https://img.shields.io/codecov/c/github/nschloe/urlchk.svg?style=flat-square)](https://app.codecov.io/gh/nschloe/urlchk)
[![LGTM](https://img.shields.io/lgtm/grade/python/github/nschloe/urlchk.svg?style=flat-square)](https://lgtm.com/projects/g/nschloe/urlchk)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

Parses text files for HTTP URLs and checks if they are still valid. Install with
```
pip install urlchk
```
and use as
```sh
urlchk README.md   # or multiple files/directories
```
To explicitly allow or ignore certain URLs, use
```
urlchk README.md -a http: -i stackoverflow.com github
```
This only considers URLs containing `http:` and _not_ containing `stackoverflow.com` or
`github`. You can also place allow and ignore lists in the config file
`~/.config/urlchk/config.toml`, e.g.,
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
urlchk -h
```
for all options.

Example output:

![](https://nschloe.github.io/urlchk/example-output-carbon.png)


### License
urlchk is published under the [MIT license](https://en.wikipedia.org/wiki/MIT_License).
