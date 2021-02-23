import xml
from pathlib import Path
import requests
import xml.etree.ElementTree as ET
import dateparser
from datetime import timedelta, datetime

# TODO: Extend to make sure that multiple feeds per company is supported.


DEBUG = False

RSS_DICT = {
    "The Apology Line": "https://rss.art19.com/apology-line",
    #"The New York Times - The Daily": "http://rss.art19.com/the-daily",
    "The Bible in a Year": "https://feeds.fireside.fm/bibleinayear/rss",
    "Crime Junkie":"https://feeds.megaphone.fm/ADL9840290619",
    "The Experiment":"http://feeds.wnyc.org/experiment_podcast"
}

# TODO: ASSUMPTION - The New York Times feed appears to be malformed from the link provided, or is huge, so I'm skipping it for the moment.
class RSSAgeChecker:
    def __init__(self):
        pass

    def check_stale_feeds(self, days: int = 3, company_dict:dict = RSS_DICT) -> dict:
        if DEBUG: print("Debug mode is active")
        companies = []
        for company, feed in company_dict.items():
            try:
                if DEBUG: print(f"Checking {company}")
                root = extract_from_url(feed)
                last_date = get_last_date(root)
                if DEBUG: print(f"Last date was {str(last_date)}")
                if check_threshold(last_date = last_date, days = days):
                    if DEBUG: print(f"{company} is stale.")
                    companies.append(company)
            except Exception as err:
                print(f"Encountered {err} with {company} from {feed}, moving on.")

        if DEBUG: print(f"Stale Companies: {str(companies)}")
        return companies


    def check_threshold(self, last_date: datetime, days: int):
        return last_date < (datetime.now(tz=last_date.tzinfo) - timedelta(days=days))


    def extract_from_url(self, rss_url: str) -> ET:
        if rss_url is None:
            return None

        resp = requests.get(rss_url)
        tree = None
        try:
            resp.raise_for_status()
            tree = ET.fromstring(resp.text)
        except Exception as err:
            print(f"{rss_url} returned bad status code {resp.status_code}")
        finally:
            return tree


    def get_last_date(self, root: ET) -> datetime:
        if root is None:
            return None

        rss_path = "./channel/item/pubDate"

        dates = root.findall(rss_path)

        # Parse Date and get last
        # TODO: ASSUMPTION: Dates may not be in time order, so searching is necessary.

        last_pubdate = None
        for date in dates:
            pubdate = dateparser.parse(date.text)
            if last_pubdate is None:
                last_pubdate = pubdate
            else:
                if pubdate > last_pubdate:
                    last_pubdate = pubdate

        return last_pubdate