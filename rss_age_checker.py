import xml
from pathlib import Path
import requests
import xml.etree.ElementTree as ET


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


def extract_from_url(rss_url: str):
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


def get_last_date(root: ET):
    # TODO: This is a scaffold
    if root is None:
        return None
    pass