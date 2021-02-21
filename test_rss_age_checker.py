from rss_age_checker import main, extract_from_url


def test_extract_smoke():
    assert extract_from_url(None) is None
    print("What")


test_extract_smoke()