import urli


def test_replace():
    content = (
        "some text\n"
        + "http://example.com\n"
        + "http://example.com/path"
    )
    d = {
        "http://example.com/path": "http://example.com/path/more",
        "http://example.com": "http://example.com/home"
    }
    new_content = urli._main.replace_in_string(content, d)

    ref = (
        "some text\n"
        + "http://example.com/home\n"
        + "http://example.com/path/more"
    )
    print(content)
    print()
    print(new_content)
    assert ref == new_content


