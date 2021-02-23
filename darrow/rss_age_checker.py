import xml
import requests
import xml.etree.ElementTree as ET
import dateparser
from datetime import timedelta, datetime



DEBUG = False

RSS_DICT = {
    "The Apology Line": "https://rss.art19.com/apology-line",
    #"The New York Times - The Daily": "http://rss.art19.com/the-daily",
    "The Bible in a Year": "https://feeds.fireside.fm/bibleinayear/rss",
    "Crime Junkie":"https://feeds.megaphone.fm/ADL9840290619",
    "The Experiment":"http://feeds.wnyc.org/experiment_podcast"
}

RSS_MIXED_DICT = {
    "Company1": [
    "https://rss.art19.com/apology-line",
    "https://feeds.fireside.fm/bibleinayear/rss"
    ],
    "Company2": "https://feeds.megaphone.fm/ADL9840290619",
    "Company3": ["http://feeds.wnyc.org/experiment_podcast" ]

}

"""
ASSUMPTION - The New York Times feed appears to be malformed from the link provided, or is huge, so I'm skipping it for the moment.

ASSUMPTION - As companies may theoretically have more than one feed, the RSS_MIXED_DICT demonstrates that variability by showing how to handle type-insecure input.

ASSUMPTION - It seems that the dates provided by the pubDate field are formatted correctly as 'aware' dates as defined by the datetime spec, meaning they represent exact times with Timezone references. This code may not work correctly if fed a pubDate field without a timezone defined. One way of dealing with this possibility would be to add heuristics to the date comparison function that will compare naive dates if necessary, and aware dates if necessary.

ASSUMPTION - Companies to Feeds is 1 to Many. If a feed contains multiple companies' feeds, this code is inaccurate. If a link represents multiple feeds, fetching the pubdates within it and searching for the latest will still provide the appropriate freshness for that company.

ASSUMPTION - Time is not a major factor in our calculations. This code operates in O(n*m) time where n is the number of companies, and m is the number of feeds in each company's entry. This could be made more efficient with asynchronous parallelism across the keys of the dictionary, but that would be best done in a compiled language, as python is limited by the GIL.

ASSUMPTION - It is assumed that by the purpose of this code, this test would be run on roughly a daily basis. Unless we check the entirety of the internet's RSS feeds, it is doubtful that we would run into time limitations based on that cadence, and even then, as the process does not block itself, unless we have overrun sufficient to crash the system, all we would have to do is modify the number of days by which to threshold the test in order to account for the time necessary to run.

ASSUMPTION - This code is assumed to be part of a pipeline or scheduled job that needs to not crash unless something truly catastrophic happens. Based on that, I have attempted to build this in such a way that errors associated with specific feeds are logged but do not crash the application.

ASSUMPTION: Dates may not be in time order, so searching is necessary. If they are in time order, the efficiency can be improved.

Theoretical improvements:

This code has been improved to be time O(n * <m) by checking the freshness of every date retrieved from the xml body as it is parsed and breaking the parsing at that point, as the desired data is at that point determined. The code as in commit (61fcd4e) is designed to allow for future extensibility for other parsing and data retrieval. The next commit (8ea5495) includes this proposed efficiency optimization.

"""
class RSSAgeChecker:
    def __init__(self, days:int = 3):
        self._days = days

    def check_stale_feeds(self, company_dict:dict = RSS_MIXED_DICT) -> dict:
        days = self._days
        if DEBUG: print("Debug mode is active")
        fresh_companies = set()
        for company, feed in company_dict.items():
            try:
                if DEBUG: print(f"Checking {company}")
                if type(feed) is str:
                    wrapped_feed = [feed]
                elif type(feed) is list:
                    wrapped_feed = feed
                for element in wrapped_feed:
                    # This is to prevent rechecking further feeds of a given company that has already been determined to be fresh.
                    if company in fresh_companies:
                        break

                    root = self.extract_from_url(element)
                    #last_date = self.get_last_date(root)
                    #if DEBUG: print(f"Last date was {str(last_date)}")
                    #if self.check_threshold(last_date = last_date, days = days):
                    if self.check_efficiently_for_first_fresh_date(root):

                        if DEBUG: print(f"{company} is fresh.")
                        fresh_companies.add(company)
            except Exception as err:
                print(f"Encountered {err} with {company} from {feed}, moving on.")

        stale_companies = set(company_dict.keys()).difference(fresh_companies)


        if DEBUG: print(f"Stale Companies: {str(stale_companies)}")

        return stale_companies

    # This method checks for if the last date is after the theshold.
    def check_threshold(self, last_date: datetime) -> bool:
        days = self._days
        return last_date > (datetime.now(tz=last_date.tzinfo) - timedelta(days=days))



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

    def check_efficiently_for_first_fresh_date(self, root: ET) -> bool:
        if root is None:
            return False

        rss_path = "./channel/item/pubDate"

        dates = root.findall(rss_path)

        # Worst case scenario = Stale - O(n * m)
        # Better case scenario = Fresh - O(n * <m)
        # Best case scenario = Fresh, Ordered - O(n * 1)

        for date in dates:
            pubdate = dateparser.parse(date.text)
            if self.check_threshold(pubdate):
                return True

        return False


    def get_last_date(self, root: ET) -> datetime:
        if root is None:
            return None

        rss_path = "./channel/item/pubDate"

        dates = root.findall(rss_path)

        # Parse Date and get last

        last_pubdate = None
        for date in dates:
            pubdate = dateparser.parse(date.text)
            if last_pubdate is None:
                last_pubdate = pubdate
            else:
                if pubdate > last_pubdate:
                    last_pubdate = pubdate

        return last_pubdate