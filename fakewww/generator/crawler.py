from urllib.request import urlopen, Request


def crawl_webpage(url):
    # TODO real crawling
    # request = urlopen(url)
    # content = request.read()
    # TODO .pre-content h1 = title
    # TODO .content without .toc-mobile = content
    return {
        'data': {
            'title': 'Lorem ipsum',
            'keywords': 'foo,bar,baz',
            'description': 'dolor sit amet',
            'content': 'Lorem ipsum dolor sit amet. Si vis pacem, para bellum. ' * 100
        },
        'links': [
            '/wiki/A',
            '/wiki/B',
        ],
    }


def crawl_website(start_url, crawler_limit):
    urls = [start_url]
    results = []
    for i in range(crawler_limit):
        url = urls.pop()
        print('[{}/{}] {}'.format(i+1, crawler_limit, url))
        crawl_result = crawl_webpage(url)
        urls.extend(crawl_result['links'])
        results.append(crawl_result['data'])
    return results
