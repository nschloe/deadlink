import deadlink


def test_check():
    out = deadlink.categorize_urls({"https://httpstat.us/200"})
    assert len(out["OK"]) == 1

    out = deadlink.categorize_urls({"https://httpstat.us/404"})
    assert len(out["Client errors"]) == 1

    # "other errors"
    out = deadlink.categorize_urls({"https://this-doesnt-exist.doesit"})
    assert len(out["Other errors"]) == 1

    # redirect
    out = deadlink.categorize_urls({"https://httpstat.us/302"})
    assert len(out["Redirects"]) == 1


def test_preserve_fragment():
    url = "http://www.numpy.org/devdocs/dev/development_workflow.html#writing-the-commit-message"
    url2 = "https://www.numpy.org/devdocs/dev/development_workflow.html#writing-the-commit-message"
    out = deadlink.categorize_urls({url})
    assert out["Redirects"][0][2] == url2


def test_relative_redirect():
    url = "http://numpy-discussion.10968.n7.nabble.com/NEP-31-Context-local-and-global-overrides-of-the-NumPy-API-tp47452p47472.html"
    url2 = "http://numpy-discussion.10968.n7.nabble.com/NEP-31-Context-local-and-global-overrides-of-the-NumPy-API-td47452.html#a47472"
    out = deadlink.categorize_urls({url})
    assert out["Redirects"][0][2] == url2
