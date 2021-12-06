import pytest

import deadlink


@pytest.mark.parametrize(
    "url,category",
    [
        ("https://httpstat.us/200", "OK"),
        ("https://httpstat.us/404", "Client errors"),
        ("https://this-doesnt-exist.doesit", "Other HTTP errors"),
        ("https://httpstat.us/301", "Successful permanent redirects"),
        ("https://httpstat.us/302", "Non-permanent redirects"),
        ("https://httpstat.us/500", "Server errors"),
        ("https://httpstat.us/200?sleep=99999", "Timeouts"),
        ("https://httpstat.us/XYZ", "Ignored"),
    ],
)
def test_check(url, category):
    print(url)
    out = deadlink.categorize_urls(
        {url}, timeout=1.0, is_allowed=lambda url: "XYZ" not in url
    )
    print(out)
    assert len(out[category]) == 1
    deadlink._main.print_to_screen(out)


def test_preserve_fragment():
    url = "http://www.numpy.org/devdocs/dev/development_workflow.html#writing-the-commit-message"
    url2 = "https://numpy.org/devdocs/dev/development_workflow.html#writing-the-commit-message"
    out = deadlink.categorize_urls({url})
    assert out["Successful permanent redirects"][0][-1].url == url2


@pytest.mark.skip("URL doesn't exist anymore")
def test_relative_redirect():
    url = "http://numpy-discussion.10968.n7.nabble.com/NEP-31-Context-local-and-global-overrides-of-the-NumPy-API-tp47452p47472.html"
    url2 = "http://numpy-discussion.10968.n7.nabble.com/NEP-31-Context-local-and-global-overrides-of-the-NumPy-API-td47452.html#a47472"
    out = deadlink.categorize_urls({url})
    assert out["Successful permanent redirects"][0][-1].url == url2
