#!/usr/bin/env python

import json
import sys

from sitemap_utils import (
    DATA_PATH,
    load_current_sitemap,
)


SITEMAP_OUT_FILE = DATA_PATH.joinpath("sitemap.json")


def write_sitemap_json(sitemap):
    """Write the sorted sitemap.json file to the repo for use in bedrock"""
    sorted_sitemap = {url: sorted(locales) for url, locales in sitemap.items()}
    with SITEMAP_OUT_FILE.open("w") as fh:
        json.dump(sorted_sitemap, fh, sort_keys=True, indent=2)


def main():
    sitemap = load_current_sitemap()
    write_sitemap_json(sitemap)


if __name__ == "__main__":
    sys.exit(main())
