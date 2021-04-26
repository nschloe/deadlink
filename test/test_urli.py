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


def test_preserve_fragment():
    url = "http://www.numpy.org/devdocs/dev/development_workflow.html#writing-the-commit-message"
    url2 = "https://www.numpy.org/devdocs/dev/development_workflow.html#writing-the-commit-message"
    out = urli.check_urls({url})
    assert out["Redirects"][0][2] == url2
