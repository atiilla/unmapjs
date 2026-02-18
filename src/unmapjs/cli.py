import argparse

from .constants import BANNER, DEFAULT_CONCURRENCY, DEFAULT_OUTPUT_DIR, __version__
from .core import UnmapJS
from .ui import print_banner


def main():
    print_banner(BANNER)

    parser = argparse.ArgumentParser(
        prog="unmapjs",
        description="Recover source files from any web app via sourcemaps",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--url", required=True,
        help="Target site URL (e.g., example.com or https://example.com)",
    )
    parser.add_argument(
        "-o", "--output", default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--include-node-modules", action="store_true",
        help="Include files from node_modules (default: skip)",
    )
    parser.add_argument(
        "--concurrency", type=int, default=DEFAULT_CONCURRENCY,
        help=f"Number of parallel download threads (default: {DEFAULT_CONCURRENCY})",
    )
    parser.add_argument(
        "--pages", metavar="FILE",
        help="File with extra paths to probe, one per line (e.g., pages.txt)",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    extra_pages = None
    if args.pages:
        with open(args.pages, "r") as f:
            extra_pages = [
                line.strip() for line in f
                if line.strip() and not line.strip().startswith("#")
            ]

    recovery = UnmapJS(
        base_url=args.url,
        output_dir=args.output,
        include_node_modules=args.include_node_modules,
        concurrency=args.concurrency,
        verbose=args.verbose,
        extra_pages=extra_pages,
    )
    recovery.run()
