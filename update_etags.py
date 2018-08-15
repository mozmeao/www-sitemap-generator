#!/usr/bin/env python

import json
import sys
from datetime import datetime, timezone
from multiprocessing.dummy import Pool as ThreadPool

import requests

from sitemap_utils import (
    CANONICAL_DOMAIN,
    SITEMAP_FILE,
    ETAGS_FILE,
    load_current_etags,
)


LOCAL_SERVER = 'http://bedrock:8000'
SITEMAP_JSON_URL = LOCAL_SERVER + '/sitemap.json'
SESSION = requests.Session()
CURRENT_ETAGS = load_current_etags()
UPDATED_ETAGS = {}
ERRORS = []
# urls to skip etag check
IGNORE = [
    '/press/speakerrequest/',
    '/press/press-inquiry/',
    '/about/legal/fraud-report/',
]


def write_new_etags(etags):
    with ETAGS_FILE.open('w') as fh:
        json.dump(etags, fh, sort_keys=True, indent=2)


def write_sitemap_json(sitemap):
    with SITEMAP_FILE.open('w') as fh:
        json.dump(sitemap, fh, sort_keys=True, indent=2)


def get_sitemap_data():
    resp = SESSION.get(SITEMAP_JSON_URL)
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
                all_urls.append('/{}{}'.format(locale, url))
        else:
            all_urls.append(url)

    return all_urls


def update_url_etag(url):
    canonical_url = CANONICAL_DOMAIN + url
    local_url = LOCAL_SERVER + url
    headers = {}
    curr_etag = CURRENT_ETAGS.get(canonical_url)
    # skip some URLs that we don't want to have lastmod dates
    if any(url.endswith(i) for i in IGNORE):
        # remove the etag and date if one already exists
        if curr_etag:
            UPDATED_ETAGS[canonical_url] = {}

        print('.', end='', flush=True)
        return

    if curr_etag:
        headers['if-none-match'] = curr_etag['etag']

    try:
        resp = SESSION.head(local_url, headers=headers)
    except requests.RequestException:
        ERRORS.append(url)
        print('x', end='', flush=True)
        return

    etag = resp.headers.get('etag')
    if etag and resp.status_code == 200:
        # sometimes the server responds with a 200 and the same etag
        if curr_etag and etag == curr_etag['etag']:
            print('.', end='', flush=True)
        else:
            UPDATED_ETAGS[canonical_url] = {
                'etag': etag,
                'date': datetime.now(timezone.utc).isoformat(),
            }
            print('*', end='', flush=True)
    else:
        if resp.status_code == 304:
            print('.', end='', flush=True)
        else:
            ERRORS.append(url)
            print('x', end='', flush=True)


def main():
    try:
        # get JSON sitemap from the site
        sitemap = get_sitemap_data()
        # mash-up the JSON data into a full list of URLs
        urls = generate_all_urls(sitemap)
        # populate UPDATED_ETAGS and ERRORS
        pool = ThreadPool(4)
        pool.map(update_url_etag, urls)
        pool.close()
        pool.join()
    except Exception as e:
        return str(e)

    if UPDATED_ETAGS:
        etags = CURRENT_ETAGS.copy()
        etags.update(UPDATED_ETAGS)
        write_new_etags(etags)
        print('\nWrote new etags.json file containing {} URLs'.format(len(etags)))

    if ERRORS:
        return '\nThe following urls returned errors:\n' + '\n'.join(ERRORS)


if __name__ == '__main__':
    sys.exit(main())
