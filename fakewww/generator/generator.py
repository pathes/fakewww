import random
import numpy as np
from numpy.random import random_sample
import re
import math

from .crawler import crawl_website
from server.models import Domain, Webpage

# Website types description:
# freq_appear - in N pages there will be usually freq_appear * N pages of this type
# pages - subpage count
# links - how much links on average page
# paragraph_size - how many words are there usually in a paragraph between links
# freq_link - dict containing probabilities of target of link on this page.
#             Note that it can link to "self", which means a link to a random subpage of this website.

WEBSITE_TYPES = {
    'big': {
        'freq_appear': 0.05,
        'pages': 40,
        'links': 10,
        'paragraph_size': 100,
        'freq_link': {
            'self': 0.5,
            'big': 0.3,
            'specialist': 0.18,
            'evil': 0.01,
            'minion': 0.01,
        },
    },
    'linking': {
        'freq_appear': 0.3,
        'pages': 5,
        'links': 6,
        'paragraph_size': 40,
        'freq_link': {
            'self': 0.4,
            'big': 0.4,
            'specialist': 0.18,
            'evil': 0.01,
            'minion': 0.01,
        },
    },
    'specialist': {
        'freq_appear': 0.1,
        'pages': 10,
        'links': 6,
        'paragraph_size': 100,
        'freq_link': {
            'self': 0.7,
            'big': 0.15,
            'specialist': 0.15,
            'evil': 0.0,
            'minion': 0.0,
        },
    },
    'evil': {
        'freq_appear': 0.1,
        'pages': 5,
        'links': 3,
        'paragraph_size': 200,
        'freq_link': {
            'self': 0.9,
            'big': 0.0,
            'specialist': 0.0,
            'evil': 0.0,
            'minion': 0.1,
        },
    },
    'minion': {
        'freq_appear': 0.45,
        'pages': 3,
        'links': 20,
        'paragraph_size': 10,
        'freq_link': {
            'self': 0.1,
            'big': 0.0,
            'specialist': 0.0,
            'evil': 0.0,
            'minion': 0.9,
        },
    },
}

WORDS = [
    re.sub('[^a-zA-Z]', '', word).lower()
    for word in
    open('/usr/share/dict/words').read().splitlines()
]


def weighted_values(values, probabilities, size):
    bins = np.add.accumulate(probabilities)
    return values[np.digitize(random_sample(size), bins)]


def random_type():
    types = list(WEBSITE_TYPES.keys())
    probabilities = [WEBSITE_TYPES[type]['freq_appear'] for type in types]
    return weighted_values(types, probabilities, 1)


def random_domain():
    return random.choice(WORDS) + random.choice(WORDS) + '.' + random.choice(['com', 'net', 'org'])


def random_path():
    n = random.randint(1, 3)
    parts = []
    for i in range(n):
        parts.append(random.choice(WORDS))
    return '/'.join(parts)


def generate_domains(domain_count):
    """
    Generates domain_count domains with random types, saves them and returns them.
    """
    domains = []
    used_names = []
    for i in range(domain_count):
        # Pick random type
        type = random_type()
        # Generate random domain name
        name = random_domain()
        while name in used_names:
            name = random_domain()
        used_names.append(name)
        # Create Domain
        domain = Domain(domain=name, type=type)
        domain.save()
        domains.append(domain)
    return domains


def generate_websites(domains, crawled_data):
    """
    Generates websites = webpages connected with domains. Webpages are initial (containing no links).
    Note that saving websites (saving each webpage) is done later in `save_websites`.
    """
    websites = {}
    for domain in domains:
        websites[domain.domain] = []
        used_paths = []
        page_count = int(WEBSITE_TYPES[domain.type]['pages'])
        # Generate main page
        # TODO change it into sitemap
        source = random.choice(crawled_data)
        webpage = Webpage(
            domain=domain,
            path='',
            title=source['title'],
            keywords=source['keywords'],
            description=source['description'],
            content=source['content'],
        )
        websites[domain.domain].append(webpage)
        # Generate subpages
        for i in range(page_count):
            # Generate random path
            path = random_path()
            while path in used_paths:
                path = random_path()
            used_paths.append(path)
            # Pick random source for content
            source = random.choice(crawled_data)
            # Create Webpage
            webpage = Webpage(
                domain=domain,
                path=path,
                title=source['title'],
                keywords=source['keywords'],
                description=source['description'],
                content=source['content'],
            )
            websites[domain.domain].append(webpage)
    return websites


def random_word_sequence(words, length):
    start = random.randint(0, len(words) - length - 1)
    return ' '.join(words[start:start+length])


def find_random_domain_and_webpage(domain, domains, websites):
    """
    Finds random domain and webpage according to freq_link distribution.
    """
    # Generate random type of webpage according to freq_link
    freq_link = WEBSITE_TYPES[domain.type]['freq_link']
    types = list(freq_link.keys())
    probabilities = [freq_link[type] for type in types]
    random_type = weighted_values(types, probabilities, 1)
    # Set random domain to itself; it can change later
    random_domain = domain
    if random_type != 'self':
        # Try to find a random domain from domains that has type=random_type
        matching_domains = list(filter(lambda d: d.type == random_type, domains))
        if len(matching_domains) > 0:
            random_domain = random.choice(matching_domains)
    # Find random webpage
    random_webpage = random.choice(websites[random_domain.domain])
    return random_domain, random_webpage


def create_html_content(domains, websites):
    """
    Creates links and HTML structure of content of websites.
    """
    # Text between links will consist of 20 to 60 words.
    i = 0
    for domain in domains:
        i += 1
        print('[{}/{}] {}'.format(i, len(domains), domain.domain))
        paragraph_size = int(WEBSITE_TYPES[domain.type]['paragraph_size'])
        paragraph_deviation = int(math.sqrt(paragraph_size))
        j = 0
        for webpage in websites[domain.domain]:
            j += 1
            print('    [{}/{}] {}/{}'.format(j, len(websites[domain.domain]), domain.domain, webpage.path))
            # After generate_websites(), their content is plaintext. We will pick parts from it.
            words = re.split('\s', webpage.content)
            webpage.content = ''
            links_left = int(WEBSITE_TYPES[domain.type]['links'])
            # Generate paragraphs each with random number of links.
            while links_left > 0:
                print(links_left)
                webpage.content += '<h2>{}</h2>'.format(random_word_sequence(words, random.randint(5, 10)))
                webpage.content += random_word_sequence(words, paragraph_size - paragraph_deviation + random.randint(0, 2*paragraph_deviation))
                links_in_paragraph = min(random.randint(1, 5), links_left)
                links_left -= links_in_paragraph
                for i in range(links_in_paragraph):
                    # Find random domain and webpage
                    random_domain, random_webpage = find_random_domain_and_webpage(domain, domains, websites)
                    # Put it in the content and add more text
                    webpage.content += ' <a href="http://{}/{}">{}</a> '.format(
                        random_domain.domain,
                        random_webpage.path,
                        random_word_sequence(words, random.randint(1, 7))
                    )
                    webpage.content += random_word_sequence(words, paragraph_size - paragraph_deviation + random.randint(0, 2*paragraph_deviation))


def save_websites(domains, websites):
    i = 0
    for domain in domains:
        i += 1
        print('[{}/{}] {}'.format(i, len(domains), domain.domain))
        for website in websites[domain.domain]:
            print('    {}/{}'.format(domain.domain, website.path))
            website.save()


def generate(domain_count, start_url, crawler_limit):
    domains = generate_domains(domain_count)
    print('\033[36mCrawling real websites...\033[39m')
    crawled_data = crawl_website(start_url, crawler_limit)
    print('\033[36mGenerating fake websites...\033[39m')
    websites = generate_websites(domains, crawled_data)
    print('\033[36mCreating HTML content...\033[39m')
    create_html_content(domains, websites)
    print('\033[36mSaving fake websites...\033[39m')
    save_websites(domains, websites)
    print('\033[36mDone generating fake websites.\033[39m')
