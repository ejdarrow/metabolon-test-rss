from rss_age_checker import main, extract_from_url, get_last_date


def test_extract_smoke():
    assert extract_from_url(None) is None

def test_request_rss():
    url = "https://rss.art19.com/apology-line"
    result = extract_from_url(url)
    assert result is not None
    assert len(str(result)) > 0

def test_find_last_date_smoke():
    url = "https://rss.art19.com/apology-line"
    result = extract_from_url(url)
    last_date = get_last_date(result)
    print(last_date)
    assert last_date is not None
    assert len(last_date) > 0

test_find_last_date_smoke()
#test_request_rss()
