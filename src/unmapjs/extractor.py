import re
from pathlib import Path

from .constants import SOURCE_PATH_PREFIXES
from .ui import log_verbose


class SourceExtractor:
    def __init__(self, output_dir, include_node_modules=False, verbose=False):
        self.output_dir = Path(output_dir)
        self.include_node_modules = include_node_modules
        self.verbose = verbose
        self.stats = {"files_recovered": 0, "files_skipped": 0, "errors": 0}

    def log(self, msg):
        if self.verbose:
            log_verbose(msg)

    def extract(self, sourcemap, sm_url):
        sources = sourcemap.get("sources", [])
        contents = sourcemap.get("sourcesContent", [])

        if not sources or not contents:
            self.log(f"No sources in {sm_url}")
            return

        for i, source_path in enumerate(sources):
            if i >= len(contents):
                break

            content = contents[i]
            if content is None:
                self.stats["files_skipped"] += 1
                continue

            cleaned = self.clean_source_path(source_path)
            if cleaned is None:
                self.stats["files_skipped"] += 1
                continue

            if not self.include_node_modules and "node_modules" in cleaned:
                self.stats["files_skipped"] += 1
                continue

            out_path = self.output_dir / cleaned
            try:
                out_path.resolve().relative_to(self.output_dir.resolve())
            except ValueError:
                self.log(f"Path traversal blocked: {cleaned}")
                self.stats["errors"] += 1
                continue

            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content, encoding="utf-8")
            self.stats["files_recovered"] += 1
            self.log(f"Recovered: {cleaned}")

    @staticmethod
    def clean_source_path(path):
        cleaned = path
        # Strip query strings (e.g., ?react, ?v=123) which are invalid in filenames
        if "?" in cleaned:
            cleaned = cleaned.split("?")[0]

        for prefix in SOURCE_PATH_PREFIXES:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
                break

        if "://" in cleaned:
            match = re.search(r'\[project\]/(.*)', cleaned)
            if match:
                cleaned = match.group(1)
            else:
                return None

        cleaned = cleaned.lstrip("./")

        if not cleaned:
            return None

        if ".." in cleaned:
            return None

        return cleaned
