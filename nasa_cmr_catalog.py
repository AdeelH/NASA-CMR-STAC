from typing import Any
from os import makedirs
from os.path import join, exists
import json
from argparse import ArgumentParser

from tqdm.auto import tqdm
import requests

URL = 'https://cmr.earthdata.nasa.gov/stac/'
TIMEOUT = 20


def main(download_dir: str,
         full: bool = False,
         force: bool = False,
         catalogs_to_skip: list[str] = []) -> None:
    catalogs = get_catalogs(URL)
    save_catalogs(catalogs, download_dir)

    with tqdm(catalogs, desc='Catalogs') as bar:
        for catalog in bar:
            if catalog in catalogs_to_skip:
                print(f'Skipping {catalog["title"]}. Ignored via --skip.')
            fetch_collections(catalog, download_dir, full=full, force=force)


def fetch_collections(catalog: dict,
                      download_dir: str,
                      full: bool = False,
                      force: bool = False) -> None:
    title = catalog['title']
    download_path = join(download_dir, f'collections_{title}.json')
    if not force and exists(download_path):
        print(f'Skipping {title}. File already exists.')
        return
    collections = get_all_collections(catalog, full=full)
    json_to_file(collections, download_path)


def get_catalogs(url: str) -> list[dict]:
    r = requests.get(url, timeout=TIMEOUT)
    data = r.json()
    catalogs = [link for link in data['links'] if link['rel'] == 'child']
    return catalogs


def get_all_collections(catalog: dict, full: bool = False) -> list[dict]:
    collections = []
    url = join(catalog['href'], 'collections')
    title = catalog['title']
    with tqdm(desc=f'Fetching {title} collections') as bar:
        while url is not None:
            r = requests.get(url, timeout=TIMEOUT)
            if r.status_code != 200:
                print(f'Status code: {r.status_code}')
                break
            data = r.json()
            page_collections = data.get('collections', [])
            if not full:
                page_collections = [{k: c[k]
                                     for k in ['id', 'title']}
                                    for c in page_collections]
            collections.extend(page_collections)
            bar.update()
            bar.set_postfix_str(f'#collections={len(collections)}')
            url = get_next_page_url(data)
    return collections


def get_next_page_url(data: dict) -> str | None:
    for link in data.get('links', []):
        if link.get('rel') == 'next':
            return link.get('href')
    return None


def json_to_file(obj: Any, path: str):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=0)


def save_catalogs(catalogs: list[dict], download_dir: str) -> None:
    catalog_names = sorted([c['title'] for c in catalogs])
    catalogs_json_path = join(download_dir, 'catalogs.json')
    json_to_file(catalogs, catalogs_json_path)
    catalog_names_path = join(download_dir, 'catalog_names.txt')
    with open(catalog_names_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(catalog_names))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        'download_dir', type=str, help='Path to download directory.')
    parser.add_argument(
        '--catalog',
        type=str,
        help='Download collections for a specific catalog.')
    parser.add_argument(
        '--full',
        action='store_true',
        help='Save the full collection metadata as opposed to '
        'just ID and title.')
    parser.add_argument(
        '--force',
        action='store_true',
        help='Download files even if they already exist.')
    parser.add_argument(
        '--skip', type=str, help='Comma-separated names of catalogs to skip.')

    opt = parser.parse_args()
    download_dir = opt.download_dir
    catalog = opt.catalog
    force = opt.force
    full = opt.full
    catalogs_to_skip = opt.skip.split(',') if opt.skip is not None else []
    makedirs(download_dir, exist_ok=True)
    if catalog is not None:
        catalogs = get_catalogs(URL)
        save_catalogs(catalogs, download_dir)
        catalog_names = [c['title'] for c in catalogs]
        fetch_collections(
            catalogs[catalog_names.index(catalog)],
            download_dir,
            full=full,
            force=force)
    else:
        main(
            download_dir=download_dir,
            full=full,
            force=force,
            catalogs_to_skip=catalogs_to_skip)
