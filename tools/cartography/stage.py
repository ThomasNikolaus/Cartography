#!/usr/bin/env python3
"""Build and validate the public Cartography files before staging a Pages site."""

import argparse
from html.parser import HTMLParser
import os
from pathlib import Path
import shutil
import stat
import sys
from urllib.parse import unquote, urljoin, urlsplit

import build


PUBLIC_FILES = ("index.html", "Style.css", "Cartography.css", "favicon-mm.png")
PUBLIC_DIRECTORIES = ("assets", "placeholders", "charts")
PUBLIC_SUFFIXES = frozenset({
    ".html", ".htm", ".pdf", ".zip", ".css", ".js", ".mjs", ".wasm",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".svg", ".ico",
    ".woff", ".woff2", ".ttf", ".otf", ".mp3", ".wav", ".ogg", ".mp4", ".webm",
})


def regular_file(path):
    """Do not follow symlinks, including broken symlinks and special files."""
    mode = path.lstat().st_mode
    if not stat.S_ISREG(mode):
        raise ValueError(f"Source must be a regular file, without symlinks: {path}")


def output_path(site_root, value):
    path = Path(value)
    if ".." in path.parts:
        raise ValueError("Output must not contain '..' path components")
    path = path if path.is_absolute() else site_root / path
    try:
        relative = path.relative_to(site_root)
    except ValueError:
        raise ValueError("Output must be inside the repository") from None
    if not relative.parts or relative.parts[0] not in {"_site", "_preview"}:
        raise ValueError("Output must be inside _site or _preview, separate from source files")
    current = site_root
    for component in relative.parts:
        current /= component
        if current.is_symlink():
            raise ValueError(f"Output must not pass through a symlink: {current}")
        if current.exists() and not current.is_dir():
            raise ValueError(f"Output path must be a directory: {current}")
    return path


def public_sources(site_root):
    """Scan every selected tree for symlinks, but publish only web file types."""
    sources = {}
    for name in (*PUBLIC_FILES, "site.json", "charts.json"):
        path = site_root / name
        regular_file(path)
        if name in PUBLIC_FILES:
            sources[name] = path
    marker = site_root / ".nojekyll"
    if marker.exists() or marker.is_symlink():
        regular_file(marker)
        sources[".nojekyll"] = marker
    else:
        sources[".nojekyll"] = None
    for name in PUBLIC_DIRECTORIES:
        directory = site_root / name
        if directory.is_symlink():
            raise ValueError(f"Source directory must not be a symlink: {directory}")
        if not directory.exists() and name == "charts":
            continue
        if not directory.is_dir():
            raise ValueError(f"Source directory is missing: {directory}")
        for parent, directories, filenames in os.walk(directory, followlinks=False):
            directories.sort()
            filenames.sort()
            for child in (*directories, *filenames):
                path = Path(parent) / child
                mode = path.lstat().st_mode
                if stat.S_ISLNK(mode) or not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                    raise ValueError(f"Source tree contains a symlink or special file: {path}")
            for filename in filenames:
                path = Path(parent) / filename
                relative = path.relative_to(site_root)
                if (any(part.startswith(".") for part in relative.parts)
                        or filename.casefold().split(".", 1)[0] in {"readme", "cname"}
                        or path.suffix.lower() not in PUBLIC_SUFFIXES):
                    continue
                sources[relative.as_posix()] = path
    return sources


class PageReferences(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.references = []
        self.anchors = set()
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "base" and "href" in attrs:
            raise ValueError("HTML base elements are unsupported; use explicit site-relative links")
        if attrs.get("id"):
            self.anchors.add(attrs["id"])
        if tag == "a" and attrs.get("name"):
            self.anchors.add(attrs["name"])
        canonical = tag == "link" and "canonical" in (attrs.get("rel") or "").lower().split()
        for attribute in ("href", "src"):
            if attrs.get(attribute) is not None:
                self.references.append((tag, attribute, attrs[attribute], canonical))


def origin(parts):
    default_port = {"https": 443, "http": 80}.get(parts.scheme.lower())
    return parts.scheme.lower(), parts.hostname, parts.port or default_port


def validate_references(sources, config):
    pages = {name: PageReferences(path.read_text(encoding="utf-8"))
             for name, path in sources.items()
             if Path(name).suffix.lower() in {".html", ".htm"}}
    expected_origin = origin(urlsplit(config["origin"]))
    prefix = config["base_path"]
    homepage_origin = origin(urlsplit(config["homepage_url"]))
    for name, page in pages.items():
        page_url = build.absolute_url(config, name)
        for tag, attribute, reference, canonical in page.references:
            try:
                original = urlsplit(reference.strip())
                target = urlsplit(urljoin(page_url, reference.strip()))
                if canonical and (target.scheme != "https" or origin(target) != expected_origin):
                    raise ValueError("Canonical URL must use the configured HTTPS origin")
                if target.scheme not in {"http", "https"} or origin(target) != expected_origin:
                    continue  # External resources are not fetched by this offline check.
                if target.username is not None or target.password is not None:
                    raise ValueError("Local URL must not include credentials")
                path = unquote(target.path, encoding="utf-8", errors="strict")
                if "\\" in path or "\x00" in path or ".." in path.split("/"):
                    raise ValueError("Local URL contains an unsafe path")
                if path == prefix:
                    relative = ""
                elif path.startswith(prefix + "/"):
                    relative = path[len(prefix) + 1:]
                else:
                    # Explicit links back to the personal homepage are outside
                    # this project's published files, even on the same domain.
                    if (tag == "a" and attribute == "href" and not canonical
                            and original.scheme == "https"
                            and origin(original) == homepage_origin):
                        continue
                    raise ValueError(f"Local URL escapes the configured base path {prefix or '/'}")
                if relative in sources:
                    destination = relative
                else:
                    destination = relative.rstrip("/") + "/index.html" if relative else "index.html"
                    if destination not in sources:
                        raise ValueError("Local reference does not resolve to a published file")
                fragment = unquote(target.fragment).split(":~:text=", 1)[0]
                if fragment and destination in pages and fragment not in pages[destination].anchors:
                    raise ValueError(f"HTML fragment does not exist: #{fragment}")
            except (ValueError, UnicodeError) as error:
                raise ValueError(f"{name}: {attribute}={reference!r}: {error}") from None


def stage(site_root, output="_site"):
    site_root = Path(site_root).resolve()
    destination = output_path(site_root, output)
    # Scan before the builder can write generated pages, and scan again afterwards.
    public_sources(site_root)
    config = build.load_config(site_root)
    chart_count = build.build(site_root)
    sources = public_sources(site_root)
    # Broken links leave any previous output untouched.
    validate_references(sources, config)
    destination.mkdir(parents=True, exist_ok=True)
    for child in destination.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()
    for name, source in sorted(sources.items()):
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if source is None:
            target.write_bytes(b"")
        else:
            regular_file(source)
            shutil.copyfile(source, target, follow_symlinks=False)
    staged = {name: destination / name for name in sources}
    validate_references(staged, config)
    return chart_count, len(staged)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="_site", help="Output directory under _site or _preview")
    arguments = parser.parse_args()
    try:
        charts, files = stage(Path(__file__).resolve().parents[2], arguments.output)
    except (ValueError, OSError) as error:
        print(f"Stage failed: {error}", file=sys.stderr)
        return 1
    print(f"Staged {charts} Charts and {files} public files into {arguments.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
