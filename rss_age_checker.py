import xml
from pathlib import Path
import requests
import xml.etree.ElementTree as ET
import dateparser
import datetime


RSS_LIST_PATH = "feeds.txt"


def main(days: int = 3) -> dict:
    feed_path = Path(RSS_LIST_PATH)
    feeds_text = feed_path.read_text()
    feeds_list = feeds_text.splitlines()
    feed_dates = {}
    for feed in feeds_list:
        root = extract_from_url(feed)
        last_date = get_last_date(root)
        if check_threshold(last_date):
            feed_dates[feed] = last_date

    print(str(feed_dates))

    return feed_dates

    # TODO: Extract more functions to make this more testable


def check_threshold(date: str):
    return True


def extract_from_url(rss_url: str) -> ET:
    # TODO: Make exception handling a little more specific.
    if rss_url is None:
        return None

    resp = requests.get(rss_url)
    try:
        resp.raise_for_status()
    except Exception as err:
        print(f"{rss_url} returned bad status code {resp.status_code}")
        return None

    return ET.fromstring(resp.text)


def get_last_date(root: ET) -> datetime:
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