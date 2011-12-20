from core.models import Image

from celery.task import task
import feedparser
import re

def reddit_pics():
    feed = feedparser.parse("http://www.reddit.com/r/pics.rss")
    link_regex = re.compile("<a href=\"(.*?)\">")
    for entry in feed.entries:
        match = re.search(r'href=[\'"]?([^\'" >]+)\"\>\[link\]', entry.description)
        Image.create_image(url=match.group(1), caption=entry.title)

@task
def scrapers():
    reddit_pics()