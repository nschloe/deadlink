<p align="center">
  <a href="https://github.com/nschloe/urli"><img alt="urli" src="https://nschloe.github.io/urli/logo-with-text.svg" width="60%"></a>
  <p align="center">The urli bird catches the worm.</p>
</p>

[![PyPi Version](https://img.shields.io/pypi/v/urli.svg?style=flat-square)](https://pypi.org/project/urli/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/urli.svg?style=flat-square)](https://pypi.org/project/urli/)
[![GitHub stars](https://img.shields.io/github/stars/nschloe/urli.svg?style=flat-square&logo=github&label=Stars&logoColor=white)](https://github.com/nschloe/urli/)
[![PyPi downloads](https://img.shields.io/pypi/dm/urli.svg?style=flat-square)](https://pypistats.org/packages/urli)

[![gh-actions](https://img.shields.io/github/workflow/status/nschloe/urli/ci?style=flat-square)](https://github.com/nschloe/urli/actions?query=workflow%3Aci)
[![codecov](https://img.shields.io/codecov/c/github/nschloe/urli.svg?style=flat-square)](https://app.codecov.io/gh/nschloe/urli)
[![LGTM](https://img.shields.io/lgtm/grade/python/github/nschloe/urli.svg?style=flat-square)](https://lgtm.com/projects/g/nschloe/urli)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

Parses text files for HTTP URLs and checks if they are still valid. Install with
```
pip install urli
```
and use as
```sh
urli README.md   # or multiple files/directories
```
To explicitly allow or ignore certain URLs, use
```
urli README.md -a http: -i stackoverflow.com github
```
This only considers URLs containing `http:` and _not_ containing `stackoverflow.com` or
`github`. You can also place allow and ignore lists in the config file
`~/.config/urli/config.toml`, e.g.,
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
urli -h
```
for all options.

Example output:

![](https://nschloe.github.io/urli/example-output-carbon.png)


### License
urli is published under the [MIT license](https://en.wikipedia.org/wiki/MIT_License).
