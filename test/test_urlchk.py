import urlchk


def test_check():
    has_errors = urlchk.check_urls({"https://www.google.com"})
    assert not has_errors

    has_errors = urlchk.check_urls({"https://github.com/nschloe/urlchk/void"})
    assert has_errors

    # "other errors"
    has_errors = urlchk.check_urls({"https://this-doesnt-exist.doesit"})
    assert has_errors

    # redirect
    has_errors = urlchk.check_urls({"https://pypi.org/pypi/pygalmesh/"})
    assert not has_errors
