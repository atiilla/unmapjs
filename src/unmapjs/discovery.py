import re
from urllib.parse import urljoin


from .ui import log_verbose


class ChunkDiscovery:
    def __init__(self, base_url, verbose=False):
        self.base_url = base_url
        self.verbose = verbose

    def log(self, msg):
        if self.verbose:
            log_verbose(msg)

    def from_html(self, html):
        urls = set()
        patterns = [
            r'(?:src|href)\s*=\s*"(/_next/static/[^"]+)"',
            r"(?:src|href)\s*=\s*'(/_next/static/[^']+)'",
            r'"(/_next/static/chunks/[^"]+\.js)"',
            r'"(/_next/static/css/[^"]+\.css)"',
            r'(?:src|href)\s*=\s*"(/(?:assets|static/js|static/css)/[^"]+)"',
            r"(?:src|href)\s*=\s*'(/(?:assets|static/js|static/css)/[^']+)'",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, html):
                path = match.group(1)
                urls.add(self.base_url + path)

        build_match = re.search(r'/_next/static/([^/]+)/_buildManifest\.js', html)
        if build_match:
            build_id = build_match.group(1)
            self.log(f"Found build ID: {build_id}")
            urls.add(f"{self.base_url}/_next/static/{build_id}/_buildManifest.js")
            urls.add(f"{self.base_url}/_next/static/{build_id}/_ssgManifest.js")

        return urls

    def from_build_manifest(self, content):
        urls = set()
        for match in re.finditer(r'"((?:static/|/_next/static/)[^"]+)"', content):
            path = match.group(1)
            if not path.startswith("/"):
                path = "/_next/" + path
            if not path.startswith("/_next/"):
                path = "/_next/static/" + path
            urls.add(self.base_url + path)
        return urls

    def from_js_content(self, content):
        urls = set()
        for match in re.finditer(
            r'["\'](_next/static/chunks/[a-f0-9]+\.js)["\']', content
        ):
            urls.add(self.base_url + "/" + match.group(1))

        for match in re.finditer(
            r'["\'](?:/_next)?(/static/chunks/[^"\']+\.(?:js|css))["\']', content
        ):
            path = match.group(1)
            if not path.startswith("/_next"):
                path = "/_next" + path
            urls.add(self.base_url + path)

        return urls

    def extract_sourcemap_url(self, content, chunk_url):
        match = re.search(r'//[#@]\s*sourceMappingURL\s*=\s*(\S+)', content)
        if not match:
            match = re.search(
                r'/\*[#@]\s*sourceMappingURL\s*=\s*(\S+)\s*\*/', content
            )
        if match:
            sm_ref = match.group(1)
            if sm_ref.startswith("data:"):
                return None
            return urljoin(chunk_url, sm_ref)
        return None
