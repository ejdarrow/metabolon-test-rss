# metabolon-test-rss
An RSS Reading tool for checking last pub dates

## Usage

Test with ./run_tests.sh

Install Dependencies with ./installer.sh

## Assumptions

Documented here as well as in the code

ASSUMPTION - The New York Times feed appears to be malformed from the link provided, or is huge, so I'm skipping it for the moment.

ASSUMPTION - Per the NYT exception, I am assuming that the standard RSS Feed format is XML, with a similar schema to the majority of the feed examples provided. If there are exceptions to this, or JSON formatted feeds, or even feeds that are so massive that they must be handled with chunking and streaming, this code does not support that at this point. That could be handled by implementing different web interfacing code that hooks directly into the XML parser and parses the content as it comes in, stopping when it encounters a date that is fresh enough the hit the threshold.

For example:

[requests - streaming](https://requests.readthedocs.io/en/master/user/quickstart/#raw-response-content)


ASSUMPTION - As companies may theoretically have more than one feed, the RSS_MIXED_DICT demonstrates that variability by showing how to handle type-insecure input.

ASSUMPTION - It seems that the dates provided by the pubDate field are formatted correctly as 'aware' dates as defined by the datetime spec, meaning they represent exact times with Timezone references. This code may not work correctly if fed a pubDate field without a timezone defined. One way of dealing with this possibility would be to add heuristics to the date comparison function that will compare naive dates if necessary, and aware dates if necessary.

ASSUMPTION - Companies to Feeds is 1 to Many. If a feed contains multiple companies' feeds, this code is inaccurate. If a link represents multiple feeds, fetching the pubdates within it and searching for the latest will still provide the appropriate freshness for that company.

ASSUMPTION - Time is not a major factor in our calculations. This code operates in O(n*m) time where n is the number of companies, and m is the number of feeds in each company's entry. This could be made more efficient with asynchronous parallelism across the keys of the dictionary, but that would be best done in a compiled language, as python is limited by the GIL.

ASSUMPTION - It is assumed that by the purpose of this code, this test would be run on roughly a daily basis. Unless we check the entirety of the internet's RSS feeds, it is doubtful that we would run into time limitations based on that cadence, and even then, as the process does not block itself, unless we have overrun sufficient to crash the system, all we would have to do is modify the number of days by which to threshold the test in order to account for the time necessary to run.

ASSUMPTION - This code is assumed to be part of a pipeline or scheduled job that needs to not crash unless something truly catastrophic happens. Based on that, I have attempted to build this in such a way that errors associated with specific feeds are logged but do not crash the application.

ASSUMPTION - Dates may not be in time order, so searching is necessary. If they are in time order, the efficiency can be improved.

## Improvements:

This code has been improved to be time O(n * <m) by checking the freshness of the dates retrieved from the xml body as it is parsed and breaking the parsing at the point of finding a fresh date, as the desired data is at that point determined. The code as in commit (61fcd4e) is designed to allow for future extensibility for other parsing and data retrieval and does not include this optimization. The next commit (8ea5495) includes this proposed efficiency optimization, and those that follow have similar improvements.

Another possible improvement would be to add further and more specific error handling and reporting. It would also be helpful to have further testing of edge cases.

It would also be helpful to understand why the New York Times feed listed in the example data is different. If that feed is too big to be handled by the requests library in any kind of reliable time, that would explain the problem. It also appears to be in HTML format when requested from a browser.


