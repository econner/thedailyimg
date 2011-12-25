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
            to_add.append((match.group(1), entry.title, 'reddit'))
    return to_add[:MAX_FROM_SOURCE]
            
def parse_from_src(url, sourcename):
    feed = feedparser.parse(url)
    to_add = []

    for entry in feed.entries:
        image_text = None
        if hasattr(entry, 'description'):
            image_text = entry.description
        elif hasattr(entry, 'value'):
            image_text = entry.value
        if not image_text: continue
        
        match = re.search(r'src=[\'"]?([^\'" >]+)', image_text)
        if match:
            print "ADDING IMAGE FROM SOURCE: ", sourcename
            to_add.append((match.group(1), entry.title, sourcename))
    return to_add[:MAX_FROM_SOURCE]

@task
def scrapers():
    to_add = []
    to_add.extend(reddit_pics())
    to_add.extend(parse_from_src("http://www.someecards.com/combined-rss", 'someecards'))
    to_add.extend(parse_from_src("http://feeds.feedburner.com/ImgurGallery?format=rss", 'imgur'))
    
    random.shuffle(to_add, random.random)
    
    for im in to_add:
        cat_ids = get_categories()
        im = Image.create_image(url=im[0], caption=im[1], source=im[2])
        if im:
            im.apply_categories(cat_ids)
    
    