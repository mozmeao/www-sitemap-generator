#!/usr/bin/env python

import asyncio
import json
import sys
from datetime import datetime, timezone

import requests
from aiohttp import ClientSession

from sitemap_utils import (
    CANONICAL_DOMAIN,
    SITEMAP_FILE,
    ETAGS_FILE,
    load_current_etags,
)


LOCAL_SERVER = 'http://bedrock:8000'
SITEMAP_JSON_URL = LOCAL_SERVER + '/sitemap.json'
UPDATED_ETAGS = {}
CURRENT_ETAGS = load_current_etags()
ERRORS = []


#####################
# Async fun
# see: https://pawelmhm.github.io/asyncio/python/aiohttp/2016/04/22/asyncio-aiohttp.html
#####################

async def fetch(url, session):
    canonical_url = CANONICAL_DOMAIN + url
    local_url = LOCAL_SERVER + url
    curr_etag = CURRENT_ETAGS.get(canonical_url)
    headers = {}
    if curr_etag:
        headers['if-none-match'] = curr_etag['etag']
    try:
        async with session.head(local_url, headers=headers) as resp:
            etag = resp.headers.get('etag')
            if etag and resp.status == 200:
                # sometimes the server responds with a 200 and the same etag
                if curr_etag and etag == curr_etag['etag']:
                    print('2', end='', flush=True)
                else:
                    UPDATED_ETAGS[canonical_url] = {
                        'etag': etag,
                        'date': datetime.now(timezone.utc).isoformat(),
                    }
                    print('*', end='', flush=True)
            else:
                if resp.status == 304:
                    print('.', end='', flush=True)
                else:
                    ERRORS.append(url)
                    print('x', end='', flush=True)
            return await resp.release()
    except Exception as e:
        print(url)
        raise


async def bound_fetch(sem, url, session):
    # Getter function with semaphore.
    async with sem:
        return await fetch(url, session)


async def fetch_etags(urls):
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(2)

    # Create client session that will ensure we dont open new connection
    # per each request.
    async with ClientSession() as session:
        for url in urls:
            # pass Semaphore and session to every request
            task = asyncio.ensure_future(bound_fetch(sem, url, session))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        await responses


#####################
# End async fun
#####################


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
                all_urls.append('/{}{}'.format(locale, url))
        else:
            all_urls.append(url)

    return all_urls


def main():
    try:
        # get JSON sitemap from the site
        sitemap = get_sitemap_data()
        # mash-up the JSON data into a full list of URLs
        urls = generate_all_urls(sitemap)
        # get the updated etags (or None if nothing updated) and error URLs
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(fetch_etags(urls))
        loop.run_until_complete(future)
    except Exception as e:
        raise
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
