import json
from pathlib import Path


CANONICAL_DOMAIN = "https://www.mozilla.org"
SITEMAP_FILE = Path("./root_files/sitemap.json")
DATA_PATH = Path("./sitemap-data")
ETAGS_FILE = DATA_PATH.joinpath("etags.json")


def load_current_etags():
    with ETAGS_FILE.open() as fh:
        etags = json.load(fh)

    return etags


def load_current_sitemap():
    with SITEMAP_FILE.open() as fh:
        sitemap = json.load(fh)

    return sitemap
