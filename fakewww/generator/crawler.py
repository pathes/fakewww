from urllib.request import urlopen
from http.client import BadStatusLine
from bs4 import BeautifulSoup
import random
from django.http import Http404

# TODO allow in future for more prefixes, maybe take down restriction
WIKI_PREFIX = 'http://en.m.wikipedia.org'
WIKI_INFIX = '/wiki/'


def crawl_webpage(url):
    if url.startswith(WIKI_INFIX):
        url = WIKI_PREFIX + url
    if not url.startswith(WIKI_PREFIX + WIKI_INFIX):
        raise Http404('fakewww crawler currently handles only pages starting with {}'.format(WIKI_PREFIX + WIKI_INFIX))

    content = urlopen(url).read()
    soup = BeautifulSoup(content)
    # Remove navigation
    nav = soup.find(class_='toc-mobile')
    if nav is not None:
        nav.extract()
    # Get title
    title = soup.find(class_='pre-content').h1.get_text()
    # Get URLs
    links = [
        a.attrs['href']
        for a in
        soup.find_all(
            'a',
            href=lambda h: (
                (h.startswith(WIKI_PREFIX + WIKI_INFIX) or h.startswith(WIKI_INFIX)) and
                (':' not in h)
            )
        )
    ]
    # Get content
    content = soup.find(class_='content').get_text()
    return {
        'data': {
            'title': title,
            'keywords': 'foo,bar,baz',
            'description': 'dolor sit amet',
            'content': content,
        },
        'links': links,
    }


def crawl_website(start_url, crawler_limit):
    urls = [start_url]
    results = []
    for i in range(crawler_limit):
        random.shuffle(urls)
        url = urls.pop()
        print('[{}/{}] {}'.format(i+1, crawler_limit, url))
        try:
            crawl_result = crawl_webpage(url)
        except BadStatusLine:
            continue
        urls.extend(crawl_result['links'])
        results.append(crawl_result['data'])
    return results
