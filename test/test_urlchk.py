import urlchk


def test_check():
    has_errors = urlchk.check_urls({"https://google.com"})
    assert not has_errors
