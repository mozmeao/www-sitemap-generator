#!/usr/bin/env python

import json
import sys
from datetime import datetime, timezone

import requests

from sitemap_utils import (
    CANONICAL_DOMAIN,
    SITEMAP_FILE,
    ETAGS_FILE,
    load_current_etags,
)


SITEMAP_JSON_URL = CANONICAL_DOMAIN + '/sitemap.json'
REQUEST_HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10.13 rv: 62.0) Gecko/20100101 Firefox/62.0'
}


def write_new_etags(etags):
    with ETAGS_FILE.open('w') as fh:
        json.dump(etags, fh, sort_keys=True, indent=2)


def write_sitemap_json(sitemap):
    with SITEMAP_FILE.open('w') as fh:
        json.dump(sitemap, fh, sort_keys=True, indent=2)


def get_sitemap_data():
    resp = requests.get(SITEMAP_JSON_URL)
    resp.raise_for_status()
    sitemap = resp.json()
    # write that data to the local repo
    write_sitemap_json(sitemap)
    return sitemap


def generate_all_urls(data):
    all_urls = []
    for url, locales in data.items():
        if locales:
            for locale in locales:
                all_urls.append('{}/{}{}'.format(CANONICAL_DOMAIN, locale, url))
        else:
            all_urls.append('{}{}'.format(CANONICAL_DOMAIN, url))

    return all_urls


def get_etags(urls):
    etags = load_current_etags()
    errors = []
    updated = False
    for url in urls:
        headers = REQUEST_HEADERS.copy()
        curr_etag = etags.get(url)
        if curr_etag:
            headers['if-none-match'] = curr_etag['etag']
        resp = requests.head(url, headers=headers)
        etag = resp.headers.get('etag')
        if etag and resp.status_code == 200:
            # sometimes the server responds with a 200 and the same etag
            if curr_etag and etag == curr_etag['etag']:
                print('.', end='', flush=True, file=sys.stderr)
            else:
                etags[url] = {
                    'etag': etag,
                    'date': datetime.now(timezone.utc).isoformat(),
                }
                updated = True
                print('*', end='', flush=True, file=sys.stderr)
        else:
            if resp.status_code == 304:
                print('.', end='', flush=True, file=sys.stderr)
            else:
                errors.append(url)
                print('x', end='', flush=True, file=sys.stderr)

    if not updated:
        etags = None

    return etags, errors


def main():
    try:
        # get JSON sitemap from the site
        sitemap = get_sitemap_data()
        # mash-up the JSON data into a full list of URLs
        urls = generate_all_urls(sitemap)
        # get the updated etags (or None if nothing updated) and error URLs
        etags, errors = get_etags(urls)
    except Exception as e:
        return str(e)

    if etags:
        write_new_etags(etags)
        print('\nWrote new etags.json file containing {} URLs'.format(len(etags)))

    if errors:
        return '\nThe following urls returned errors:\n' + '\n'.join(errors)


if __name__ == '__main__':
    sys.exit(main())
