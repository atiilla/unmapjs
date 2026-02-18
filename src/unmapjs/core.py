from urllib.parse import urlparse

from .constants import PROBE_PATHS
from .discovery import ChunkDiscovery
from .downloader import Downloader
from .extractor import SourceExtractor
from .ui import C, Spinner, ProgressBar, log_verbose


class UnmapJS:
    def __init__(self, base_url, output_dir, include_node_modules=False,
                 concurrency=10, verbose=False, extra_pages=None):
        parsed = urlparse(base_url)
        if not parsed.scheme:
            base_url = "https://" + base_url
        self.base_url = base_url.rstrip("/")
        self.verbose = verbose
        self.extra_pages = extra_pages

        self.downloader = Downloader(concurrency=concurrency, verbose=verbose)
        self.discovery = ChunkDiscovery(self.base_url, verbose=verbose)
        self.extractor = SourceExtractor(
            output_dir, include_node_modules=include_node_modules, verbose=verbose
        )

        self.discovered_chunks = set()
        self.sourcemap_urls = set()

    def log(self, msg):
        if self.verbose:
            log_verbose(msg)

    def run(self):
        print(f"  {C.DIM}Target{C.RESET}  {C.BRIGHT_WHITE}{self.base_url}{C.RESET}")
        print(f"  {C.DIM}Output{C.RESET}  {C.BRIGHT_WHITE}{self.extractor.output_dir}{C.RESET}\n")

        # Step 1: Discover entry points
        with Spinner("Discovering entry points...") as sp:
            self._discover_entry_points()
            sp.stop(f"Discovered {C.BRIGHT_CYAN}{len(self.discovered_chunks)}{C.RESET} chunk URLs")

        if not self.discovered_chunks:
            print(f"  {C.RED}✗{C.RESET} No chunks discovered. Exiting.")
            return

        # Step 2: Download chunks & extract sourcemap URLs
        self._process_chunks()

        if not self.sourcemap_urls:
            print(f"  {C.RED}✗{C.RESET} No sourcemaps found. The site may not expose them.")
            return

        # Step 3: Download sourcemaps
        self._download_sourcemaps()

        # Step 4: Extract source files
        with Spinner("Extracting source files...") as sp:
            self.extractor.output_dir.mkdir(parents=True, exist_ok=True)
            for sm_url, sm_data in self.sourcemaps.items():
                self.extractor.extract(sm_data, sm_url)
            stats = self.extractor.stats
            sp.stop(f"Extracted {C.BRIGHT_CYAN}{stats['files_recovered']}{C.RESET} files")

        # Summary
        stats = self.extractor.stats
        print()
        print(f"  {C.GREEN}Files recovered{C.RESET}  {C.BRIGHT_WHITE}{stats['files_recovered']}{C.RESET}")
        print(f"  {C.YELLOW}Files skipped{C.RESET}    {C.BRIGHT_WHITE}{stats['files_skipped']}{C.RESET}")
        print(f"  {C.RED}Errors{C.RESET}           {C.BRIGHT_WHITE}{stats['errors']}{C.RESET}")
        print(f"  {C.DIM}Output{C.RESET}           {C.BRIGHT_WHITE}{self.extractor.output_dir}{C.RESET}")

    def _discover_entry_points(self):
        html = self.downloader.fetch(self.base_url)
        if html:
            self.discovered_chunks.update(self.discovery.from_html(html))

        probe_paths = list(PROBE_PATHS)
        if self.extra_pages:
            probe_paths.extend(self.extra_pages)

        for path in probe_paths:
            if not path.startswith("/"):
                path = "/" + path
            page_html = self.downloader.fetch(self.base_url + path)
            if page_html:
                self.discovered_chunks.update(self.discovery.from_html(page_html))

        manifest_urls = [u for u in self.discovered_chunks if "_buildManifest" in u]
        for manifest_url in manifest_urls:
            content = self.downloader.fetch(manifest_url)
            if content:
                self.discovered_chunks.update(
                    self.discovery.from_build_manifest(content)
                )

    def _process_chunks(self):
        processed = set()
        to_process = set(self.discovered_chunks)

        total = len(to_process)
        bar = ProgressBar("Downloading chunks", total)

        while to_process:
            batch = to_process - processed
            if not batch:
                break

            results = self.downloader.fetch_many(batch)
            for url, content in results.items():
                processed.add(url)
                sm_url = self.discovery.extract_sourcemap_url(content, url)
                if sm_url:
                    self.sourcemap_urls.add(sm_url)
                new_chunks = self.discovery.from_js_content(content)
                to_process.update(new_chunks)
                self.discovered_chunks.update(new_chunks)

            processed.update(batch)

            bar.total = len(self.discovered_chunks)
            bar.update(len(processed))

        bar.finish(
            f"Downloaded {C.BRIGHT_CYAN}{len(processed)}{C.RESET} chunks, "
            f"found {C.BRIGHT_CYAN}{len(self.sourcemap_urls)}{C.RESET} sourcemaps"
        )

    def _download_sourcemaps(self):
        total = len(self.sourcemap_urls)
        bar = ProgressBar("Downloading sourcemaps", total)

        def progress(url, result, done, total):
            bar.update(done)

        self.sourcemaps = self.downloader.fetch_many(
            self.sourcemap_urls, callback=progress, json_mode=True
        )
        bar.finish(f"Downloaded {C.BRIGHT_CYAN}{len(self.sourcemaps)}{C.RESET} sourcemaps")
