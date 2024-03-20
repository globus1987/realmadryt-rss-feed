import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Replace 'your_website_url' with the website you want to scrape
url = 'https://www.realmadryt.pl/aktualnosci'

response = requests.get(url)
response.encoding = 'utf-8'  # ensure correct encoding
soup = BeautifulSoup(response.content, 'html.parser')

# Find the news items - you'll need to update the selectors based on the website's structure
news_items = soup.select('.news-article')

rss_items = []

for item in news_items:
    title = item.select_one('h4').text.strip()
    description = item.select_one('p').text.strip()
    link = 'https://www.realmadryt.pl' + item.select_one('a')['href']
    date = item.select_one('h6 span').text.strip()
    date_object = datetime.strptime(date, "%Y.%m.%d, %H:%M")

    # Optional: If available, you can also fetch the publication date and description
    pub_date = date_object.strftime('%a, %d %b %Y %H:%M:%S GMT')

    rss_item = f"""
    <item>
        <title>{title}</title>
        <link>{link}</link>
        <pubDate>{pub_date}</pubDate>
        <description>{description}</description>
    </item>
    """
    rss_items.append(rss_item)

# RSS Feed Template
rss_feed_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>RealMadryt.pl custom feed</title>
    <link>{url}</link>
    <description>Custom feed from realmadryt.pl</description>
    <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>
    {''.join(rss_items)}
</channel>
</rss>
"""

# Print or save your RSS feed
print(rss_feed_template)
# Optionally, save the feed to a file
with open('custom_feed.xml', 'w', encoding='utf-8') as file:
    file.write(rss_feed_template)
