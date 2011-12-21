from core.models import Image, Category

from celery.task import task
import feedparser
import re

def reddit_pics():
    feed = feedparser.parse("http://www.reddit.com/r/pics.rss")
    link_regex = re.compile("<a href=\"(.*?)\">")
    
    cat_titles = ['Funny', 'Interesting', 'Inspiring', 'Powerful']
    cat_ids = []
    for cat_title in cat_titles:
        c = Category.objects.get(title=cat_title)
        cat_ids.append(c.pk)
    
    for entry in feed.entries:
        match = re.search(r'href=[\'"]?([^\'" >]+)\"\>\[link\]', entry.description)
        im = Image.create_image(url=match.group(1), caption=entry.title)
        if im:
            im.apply_categories(cat_ids)

@task
def scrapers():
    reddit_pics()