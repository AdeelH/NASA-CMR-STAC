# NASA-CMR-STAC

Forked from [opengeos/NASA-CMR-STAC](https://github.com/opengeos/NASA-CMR-STAC).

## Introduction

NASA's [Common Metadata Repository (CMR)](https://cmr.earthdata.nasa.gov/) is a metadata catalog of NASA Earth Science data. This repo compiles the list of all geospatial datasets on [CMR-STAC](https://wiki.earthdata.nasa.gov/display/ED/CMR+SpatioTemporal+Asset+Catalog+%28CMR-STAC%29+Documentation) as JSON files, which allows collections to be searched by ID or title.

## Usage

```sh
$ python nasa_cmr_catalog.py --help
# usage: nasa_cmr_catalog.py [-h] [--catalog CATALOG] [--full] [--force] [--skip SKIP] download_dir

# positional arguments:
#   download_dir       Path to download directory.

# options:
#   -h, --help         show this help message and exit
#   --catalog CATALOG  Download collections for a specific catalog.
#   --full             Save the full collection metadata as opposed to just ID and title.
#   --force            Download files even if they already exist.
#   --skip SKIP        Comma-separated names of catalogs to skip.
```
