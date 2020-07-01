import json
from pathlib import Path


CANONICAL_DOMAIN = 'https://www.mozilla.org'
SITEMAP_FILE = Path('./root_files/sitemap.json')
ETAGS_FILE = Path('./sitemap-data/etags.json')


def load_current_etags():
    with ETAGS_FILE.open() as fh:
        etags = json.load(fh)

    return etags


def load_current_sitemap():
    with SITEMAP_FILE.open() as fh:
        sitemap = json.load(fh)

    return sitemap


def generate_all_urls(data):
    all_urls = {}
    for url, locales in data.items():
        if locales:
            for locale in locales:
                all_urls.append('{}/{}{}'.format(CANONICAL_DOMAIN, locale, url))
        else:
            all_urls.append('{}{}'.format(CANONICAL_DOMAIN, url))

    return all_urls
