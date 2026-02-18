import json
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from .constants import DEFAULT_TIMEOUT, DEFAULT_USER_AGENT, SOURCEMAP_TIMEOUT
from .ui import log_verbose


class Downloader:
    def __init__(self, concurrency=10, verbose=False):
        self.concurrency = concurrency
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": DEFAULT_USER_AGENT})

    def log(self, msg):
        if self.verbose:
            log_verbose(msg)

    def fetch(self, url, timeout=DEFAULT_TIMEOUT):
        try:
            resp = self.session.get(url, timeout=timeout, allow_redirects=True)
            if resp.status_code == 200:
                return resp.text
            self.log(f"HTTP {resp.status_code} for {url}")
        except requests.RequestException as e:
            self.log(f"Error fetching {url}: {e}")
        return None

    def fetch_json(self, url, timeout=SOURCEMAP_TIMEOUT):
        try:
            resp = self.session.get(url, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
            self.log(f"HTTP {resp.status_code} for {url}")
        except (requests.RequestException, json.JSONDecodeError) as e:
            self.log(f"Error fetching {url}: {e}")
        return None

    def fetch_many(self, urls, callback=None, json_mode=False):
        results = {}
        fetch_fn = self.fetch_json if json_mode else self.fetch
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            futures = {executor.submit(fetch_fn, url): url for url in urls}
            done = 0
            total = len(futures)
            for future in as_completed(futures):
                url = futures[future]
                done += 1
                try:
                    result = future.result()
                    if result is not None:
                        results[url] = result
                    if callback:
                        callback(url, result, done, total)
                except Exception as e:
                    self.log(f"Error downloading {url}: {e}")
                    if callback:
                        callback(url, None, done, total)
        return results
