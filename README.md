```
atilla@ubuntu:~/$ unmapjs --help
 _   _ _ __  _ __ ___   __ _ _ __ (_)___
| | | | '_ \| '_ ` _ \ / _` | '_ \| / __|
| |_| | | | | | | | | | (_| | |_) | \__ \
 \__,_|_| |_|_| |_| |_|\__,_| .__// |___/
                            |_| |__/
      github: @atiilla

usage: unmapjs [-h] [--version] --url URL [-o OUTPUT] [--include-node-modules] [--concurrency CONCURRENCY] [--pages FILE] [--verbose]

Recover source files from any web app via sourcemaps

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --url URL             Target site URL (e.g., example.com or https://example.com)
  -o OUTPUT, --output OUTPUT
                        Output directory (default: ./recovered-source)
  --include-node-modules
                        Include files from node_modules (default: skip)
  --concurrency CONCURRENCY
                        Number of parallel download threads (default: 10)
  --pages FILE          File with extra paths to probe, one per line (e.g., pages.txt)
  --verbose             Enable verbose output
```

> CLI to unpack your js source maps to original files and folders.

**unmapjs** automatically discovers, downloads, and extracts original source code from JavaScript source maps exposed by React, Next.js, Vite, Webpack, Rollup, and Turbopack applications.

## Features

- Discovers JS chunks and sourcemap references from any URL
- Supports Next.js `_buildManifest`, Webpack, Vite, Rollup, and Turbopack prefixes
- Recursively follows chunk references to find all sourcemaps
- Parallel downloads with configurable concurrency
- Animated progress bars and spinners
- Custom page list support (`--pages pages.txt`) for targeted discovery
- Filters out `node_modules` by default
- Path traversal protection on extracted files

## Installation

```bash
pip install unmapjs
```

Or install from source:

```bash
git clone https://github.com/intelseclab/unmapjs.git
cd unmapjs
pip install .
```

## Usage

```bash
unmapjs --url example.com
```

```bash
unmapjs --url https://example.com -o ./output --verbose
```

With a custom pages file:

```bash
unmapjs --url example.com --pages pages.txt
```

Where `pages.txt` contains paths to probe (one per line, lines starting with `#` are ignored):

```
# auth pages
/login
/signup
/forgot-password
# app routes
/dashboard
/settings
/api/docs
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--url` | Target site URL | *required* |
| `-o, --output` | Output directory | `./recovered-source` |
| `--concurrency` | Parallel download threads | `10` |
| `--pages FILE` | File with extra paths to probe, one per line | |
| `--include-node-modules` | Include `node_modules` files | `false` |
| `--verbose` | Enable verbose output | `false` |
| `--version` | Show version | |

## How It Works

1. **Discover** — Fetches the target URL and common pages (`/login`, `/signup`, `/dashboard`, etc.) to find JS/CSS chunk references
2. **Download chunks** — Downloads all discovered chunks and extracts `sourceMappingURL` references
3. **Download sourcemaps** — Fetches all referenced `.map` files
4. **Extract** — Unpacks original source files from `sourcesContent` and writes them to disk with their original directory structure

## Supported Bundlers

| Bundler | Prefix |
|---------|--------|
| Webpack | `webpack:///` |
| Next.js (Webpack) | `webpack:///_N_E/` |
| Turbopack | `turbopack:///[project]/` |
| Vite | `vite:///` |
| Rollup | `rollup:///` |

## Disclaimer

This tool is intended for **authorized security testing**, **bug bounty research**, and **educational purposes** only. Only use it on applications you have permission to test. The author is not responsible for any misuse.

## License

MIT
