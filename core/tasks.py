from core.models import Image, Category

from celery.task import task
import feedparser
import re
import random

MAX_FROM_SOURCE = 25

def get_categories():
    cat_titles = ['Funny', 'Interesting', 'Inspiring', 'Powerful']
    cat_ids = []
    for cat_title in cat_titles:
        c = Category.objects.get(title=cat_title)
        cat_ids.append(c.pk)
    return cat_ids

def reddit_pics():
    feed = feedparser.parse("http://www.reddit.com/r/pics.rss")
    
    to_add = []
    for entry in feed.entries:
        match = re.search(r'href=[\'"]?([^\'" >]+)\"\>\[link\]', entry.description)
        if match:
            to_add.append((match.group(1), entry.title))
    return to_add[:MAX_FROM_SOURCE]
            
def someecards_pics():
    feed = feedparser.parse("http://www.someecards.com/combined-rss")
    to_add = []

    for entry in feed.entries:
        match = re.search(r'src=[\'"]?([^\'" >]+)', entry.description)
        if match:
            to_add.append((match.group(1), entry.title))
    return to_add[:MAX_FROM_SOURCE]

@task
def scrapers():
    to_add = []
    to_add.extend(reddit_pics())
    to_add.extend(someecards_pics())
    
    random.shuffle(to_add, random.random)
    
    for im in to_add:
        cat_ids = get_categories()
        im = Image.create_image(url=im[0], caption=im[1])
        if im:
            im.apply_categories(cat_ids)
    
    