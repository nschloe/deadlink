import urli


def test_check():
    out = urli.check_urls({"https://www.google.com"})
    assert len(out["OK"]) == 1

    out = urli.check_urls({"https://github.com/nschloe/urli/void"})
    assert len(out["Client errors"]) == 1

    # "other errors"
    out = urli.check_urls({"https://this-doesnt-exist.doesit"})
    assert len(out["Other errors"]) == 1

    # redirect
    out = urli.check_urls({"https://pypi.org/pypi/pygalmesh/"})
    assert len(out["Redirects"]) == 1
