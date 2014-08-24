import random
import numpy as np
from numpy.random import random_sample
import re

from .crawler import crawl_website
from server.models import Domain, Webpage

# Website types description:
# freq_appear - in N pages there will be usually freq_appear * N pages of this type
# pages - subpage count
# links - how much links on average page
# freq_link - dict containing probabilities of target of link on this page.
#             Note that it can link to "self", which means a link to a random subpage of this website.

WEBSITE_TYPES = {
    'big': {
        'freq_appear': 0.05,
        'pages': 100,
        'links': 10,
        'freq_link': {
            'self': 0.5,
            'big': 0.3,
            'specialist': 0.18,
            'evil': 0.01,
            'minion': 0.01,
        }
    },
    'linking': {
        'freq_appear': 0.3,
        'pages': 5,
        'freq_link': {
            'self': 0.4,
            'big': 0.4,
            'specialist': 0.18,
            'evil': 0.01,
            'minion': 0.01,
        }
    },
    'specialist': {
        'freq_appear': 0.1,
        'pages': 15,
        'freq_link': {
            'self': 0.7,
            'big': 0.15,
            'specialist': 0.15,
            'evil': 0.0,
            'minion': 0.0,
        }
    },
    'evil': {
        'freq_appear': 0.1,
        'pages': 5,
        'freq_link': {
            'self': 0.9,
            'big': 0.0,
            'specialist': 0.0,
            'evil': 0.0,
            'minion': 0.1,
        }
    },
    'minion': {
        'freq_appear': 0.45,
        'pages': 5,
        'freq_link': {
            'self': 0.1,
            'big': 0.0,
            'specialist': 0.0,
            'evil': 0.0,
            'minion': 0.9,
        }
    },
}

WORDS = [
    re.sub('[^a-z]', '', word)
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


def create_links(websites):
    # TODO create links with beautifulsoup4
    # TODO remember about creating many internal links in page with path=''
    pass


def save_websites(domains, websites):
    print('\033[36mSaving websites...\033[39m')
    i = 0
    for domain in domains:
        i += 1
        print('[{}/{}] {}'.format(i, len(domains), domain.domain))
        for website in websites[domain.domain]:
            print('    {}/{}'.format(domain.domain, website.path))
            website.save()


def generate(domain_count, start_url, crawler_limit):
    domains = generate_domains(domain_count)
    crawled_data = crawl_website(start_url, crawler_limit)
    websites = generate_websites(domains, crawled_data)
    #create_links(websites)
    save_websites(domains, websites)
    print('\033[36mDone generating websites.\033[39m')
