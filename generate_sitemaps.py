#!/usr/bin/env python

import sys
from pathlib import Path
from operator import itemgetter

from jinja2 import Environment, FileSystemLoader

from sitemap_utils import (
    CANONICAL_DOMAIN,
    load_current_etags,
    load_current_sitemap,
)


SITEMAPS_PATH = Path('./sitemaps')
env = Environment(loader=FileSystemLoader('./templates'))


def write_sitemaps(all_urls):
    for locale, urls in all_urls.items():
        if locale != 'none':
            output_file = SITEMAPS_PATH.joinpath(locale, 'sitemap.xml')
            output_file.parent.mkdir(exist_ok=True)
        else:
            output_file = SITEMAPS_PATH.joinpath('sitemap_none.xml')

        template = env.get_template('sitemap.xml')
        template.stream({'paths': sorted(urls, key=itemgetter('url'))}).dump(str(output_file))

    output_file = SITEMAPS_PATH.joinpath('sitemap.xml')
    template = env.get_template('sitemap_index.xml')
    template.stream({
        'canonical_url': CANONICAL_DOMAIN,
        'locales': sorted(all_urls.keys())
    }).dump(str(output_file))


def get_urls_by_locale(sitemap, etags):
    urls_by_locale = {}
    for url, locales in sitemap.items():
        if not locales:
            locales = ['none']

        for locale in locales:
            urls_by_locale.setdefault(locale, [])
            if locale == 'none':
                full_url = CANONICAL_DOMAIN + url
            else:
                full_url = '{}/{}{}'.format(CANONICAL_DOMAIN, locale, url)

            data = {'url': full_url}
            etag = etags.get(full_url)
            if etag:
                data['lastmod'] = etag['date']
            urls_by_locale[locale].append(data)

    return urls_by_locale


def main():
    etags = load_current_etags()
    sitemap = load_current_sitemap()
    urls_by_locale = get_urls_by_locale(sitemap, etags)
    print(urls_by_locale)
    write_sitemaps(urls_by_locale)


if __name__ == '__main__':
    sys.exit(main())
