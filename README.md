# www-sitemap-generator

A tool for ingesting the sitemap.json file from www.mozilla.org and creating
[sitemap protocol](https://www.sitemaps.org/) compatible XML files with lastmod
datetimes based on changes to etags.

## Usage

```bash
$ ./generate_sitemap_docker.sh
```

This will build the docker image, run `update_etags.py` which gets https://www.mozilla.org/sitemap.json,
saves it, then uses that data to do `GET` requests against all of the URLs to get and compare the
[etags](https://en.wikipedia.org/wiki/HTTP_ETag) in the responses, and then run `generate_sitemaps.py`
which takes the data saved by `update_etags.py` and generates the XML sitemaps for use on the site.
