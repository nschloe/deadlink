import urlchk


def test_check():
    has_errors = urlchk.check_urls({"https://www.google.com"})
    assert not has_errors

    has_errors = urlchk.check_urls({"https://this-doesnt-exist.doesit"})
    assert has_errors
