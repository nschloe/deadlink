# urlchk

[![PyPi Version](https://img.shields.io/pypi/v/urlchk.svg?style=flat-square)](https://pypi.org/project/urlchk)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/urlchk.svg?style=flat-square)](https://pypi.org/pypi/urlchk/)
[![GitHub stars](https://img.shields.io/github/stars/nschloe/urlchk.svg?style=flat-square&logo=github&label=Stars&logoColor=white)](https://github.com/nschloe/urlchk)
[![PyPi downloads](https://img.shields.io/pypi/dm/urlchk.svg?style=flat-square)](https://pypistats.org/packages/urlchk)

[![gh-actions](https://img.shields.io/github/workflow/status/nschloe/urlchk/ci?style=flat-square)](https://github.com/nschloe/urlchk/actions?query=workflow%3Aci)
[![CircleCI](https://img.shields.io/circleci/project/github/nschloe/urlchk/main.svg?style=flat-square)](https://circleci.com/gh/nschloe/urlchk/tree/main)
[![travis](https://img.shields.io/travis/nschloe/urlchk.svg?style=flat-square)](https://travis-ci.org/nschloe/urlchk)
[![codecov](https://img.shields.io/codecov/c/github/nschloe/urlchk.svg?style=flat-square)](https://codecov.io/gh/nschloe/urlchk)
[![LGTM](https://img.shields.io/lgtm/grade/python/github/nschloe/urlchk.svg?style=flat-square)](https://lgtm.com/projects/g/nschloe/urlchk)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)


A Python project template that highlights some best practices in Python packaging. Can
be used as a [GitHub
template](https://github.blog/2019-06-06-generate-new-repositories-with-repository-templates/)
for your new Python project.

### Best practices

* The **name** of the Git repository should be the PyPi name of the package and should
  be what you type as `import mypackagename`. That means no hyphens in package
  names!

* Your package should be a **one-trick pony**. Nobody wants to install a huge toolbox if
  all they need is the image converter in it.

* After `import yourpackagename`, people should be able to call
  `yourpackagename.__version__`. This helps with debugging.

* Choose a **license** for your code and provide a `LICENSE[.txt]` in the root level of
  your package as well as a statement in your main README.
  [choosealicense.com](https://choosealicense.com/) can help you make a decision.

* Use **linting and formatting**, include those in your integration tests.
    - [black](https://github.com/python/black) is a formatter that I like because you
      cannot configure it -- black is black.
    - Good linters are [flake8](http://flake8.pycqa.org/en/latest/) and
      [pylint](https://www.pylint.org/).
    - [isort](https://pypi.org/project/isort/) sorts your imports.

* Once you have tests in order, make sure they are executed with every git push.
  Popular **CI services** that run your tests are [GitHub
  Actions](https://github.com/features/actions), [Travis CI](https://travis-ci.org/),
  and [CircleCI](https://circleci.com/). This repository contains the config files for
  each of them.

* Make sure that **nobody can push to main**. On GitHub, go to Settings -> Branches ->
  Add rule and select _Require status checks to pass before merging_ and _Include
  administrators_. Development happens in pull requests, this makes sure that nobody --
  including yourself -- ever accidentally pushes something broken to main.

* Use a tool for measuring **test coverage**. [codecov](https://codecov.io/) is one, and
  your CI provider submits the data to it.

* If you have CI set up, want to show test coverage, or advertise
  the availability on PyPi, do so using a **badge** at the top of your README. Check out
  [shields.io](https://shields.io/) for what's available.

* Include [**contributing guidelines**](CONTRIBUTING.md) and a [**code of
  conduct**](CODE_OF_CONDUCT.md) (edit to add appropriate
  [enforcement](CODE_OF_CONDUCT.md#enforcement) contacts or [use a
  template](https://help.github.com/en/articles/adding-a-code-of-conduct-to-your-project))
  to help foster a community.

### What you can do with this template

First run
```
find . -type f -print0 -name "*.py" -o -name Makefile -o -name "*.yml" | xargs -0 sed -i 's/urlchk/your-project-name/g'
```
and rename the folder `urlchk` to customize the name.

There is a simple `Makefile` that can help you with certain tasks:
  * Run `make format` to apply formatting.
  * Run `make lint` to check formatting and style.
  * Run `make publish` to
     - tag your project on git (`make tag`)
     - upload your package to PyPi (`make upload`)

    After publishing, people can install your package with
    ```
    pip3 install urlchk
    ```

### Testing

To run the urlchk unit tests, check out this repository and do
```
tox
```

### License

urlchk is published under the [MIT license](https://en.wikipedia.org/wiki/MIT_License).
