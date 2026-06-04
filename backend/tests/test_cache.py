from cache import _slugify


def test_slugify_simple():
    assert _slugify("San Francisco, CA") == "san-francisco-ca"


def test_slugify_no_commas():
    assert _slugify("New York") == "new-york"


def test_slugify_special_chars():
    assert _slugify("Minneapolis/St. Paul") == "minneapolisst-paul"
