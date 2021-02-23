from darrow import RSSAgeChecker
import pytest

# TODO: More Unit Tests would be better.

class TestRSSAgeChecker:
    checker = RSSAgeChecker()

    def test_extract_smoke(self):
        assert self.checker.extract_from_url(None) is None

    def test_request_rss(self):
        url = "https://rss.art19.com/apology-line"
        result = self.checker.extract_from_url(url)
        assert result is not None
        assert len(str(result)) > 0

    def test_find_last_date_smoke(self):
        url = "https://rss.art19.com/apology-line"
        result = self.checker.extract_from_url(url)
        last_date = self.checker.get_last_date(result)
        assert last_date is not None

    def test_check_stale_feeds(self):
        stale_companies = self.checker.check_stale_feeds()
        #print(str(stale_companies))
        assert stale_companies is not None

