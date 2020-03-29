## CheggScraper
### What is Cheggscraper?
CheggScraper is an application purpose built to scrape all questions and answers from [chegg.com](https://www.chegg.com).

### Use
**Package requirements**

Uses python 3.6+
1. `pip install beautifulsoup4`
2. `pip install numpy`
3. `pip install selenium`

Optional imports:
1. `pip install fake_useragent`
Note: Fake user agent is not required, and seems to actually improve PerimeterX's ability to block the program in most cases.

Run scraper.py in terminal or using an IDE like PyCharm

`M` Select which operating system you are using, supports most Linux64 and Windows 10

`B` You can roll backwards or forwards in the question list by
restarting the program and manually setting the counter position
Note: This will not overwrite existing data written to a csv or specified database

`Q` Terminates the CheggScraper process

`S` Generate a random list of questions and begin scraping chegg.com

### Notes
* Uses uMatrix to block the Chegg CDN before it loads PerimeterX. PerimeterX is delivered through the CDN to
increase the responsiveness of Chegg, but is ultimately a vulnerability that allows this bot to function.
* Now fully supports google chrome instead of just chromium
* Make sure to use a VPN, because they should still be able to ban by IP after seeing excess web traffic
