#!/usr/bin/env python3
"""Validate the deployed ArSonKuPik canonical SEO contract.

Cloudflare Pages is the canonical public host. GitHub Pages remains an
accessible mirror and must advertise the same Cloudflare canonical URLs.
"""
from __future__ import annotations

import argparse
import json
import struct
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

PRIMARY_ROOT = "https://arsonkupik.pages.dev/"
MIRROR_ROOT = "https://masarray.github.io/vst-enhancer/"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
SOCIAL_PATH = "assets/arsonkupik-guide-social-1200x630.png"
VERIFY_PATH = "googlec34c43149eef6100.html"

PAGE_SPECS = [
    ("", "site/index.html", "en", "", "id/", {"WebSite", "WebPage", "SoftwareApplication"}),
    ("id/", "site/id/index.html", "id", "", "id/", {"WebPage", "SoftwareApplication"}),
    ("guide/", "site/guide/index.html", "en", "guide/", "id/guide/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    ("id/guide/", "site/id/guide/index.html", "id", "guide/", "id/guide/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    ("activation/", "site/activation/index.html", "en", "activation/", "id/activation/", {"WebPage"}),
    ("id/activation/", "site/id/activation/index.html", "id", "activation/", "id/activation/", {"WebPage"}),
    ("about/", "site/about/index.html", "en", "about/", "id/about/", {"AboutPage", "WebPage", "BreadcrumbList"}),
    ("id/about/", "site/id/about/index.html", "id", "about/", "id/about/", {"AboutPage", "WebPage", "BreadcrumbList"}),
    ("measurements/", "site/measurements/index.html", "en", "measurements/", "id/measurements/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    ("id/measurements/", "site/id/measurements/index.html", "id", "measurements/", "id/measurements/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    ("audio-comparisons/", "site/audio-comparisons/index.html", "en", "audio-comparisons/", "id/audio-comparisons/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    ("id/audio-comparisons/", "site/id/audio-comparisons/index.html", "id", "audio-comparisons/", "id/audio-comparisons/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    ("use-cases/windows-system-audio/", "site/use-cases/windows-system-audio/index.html", "en", "use-cases/windows-system-audio/", "id/use-cases/windows-system-audio/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    ("id/use-cases/windows-system-audio/", "site/id/use-cases/windows-system-audio/index.html", "id", "use-cases/windows-system-audio/", "id/use-cases/windows-system-audio/", {"TechArticle", "WebPage", "BreadcrumbList"}),
]


def root(value: str) -> str:
    value = value.strip().rstrip("/") + "/"
    if not value.startswith("https://"):
        raise ValueError("SEO roots must use https://")
    return value


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, "Unexpected redirect", headers, fp)


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.lang = ""
        self.h1 = 0
        self.meta: dict[str, list[str]] = defaultdict(list)
        self.props: dict[str, list[str]] = defaultdict(list)
        self.canonical: list[str] = []
        self.sitemap: list[str] = []
        self.hreflang: dict[str, str] = {}
        self.json_ld: list[object] = []
        self._json = False
        self._chunks: list[str] = []

    def handle_starttag(self, tag, attrs) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag == "html":
            self.lang = data.get("lang", "").lower()
        elif tag == "h1":
            self.h1 += 1
        elif tag == "meta":
            if data.get("name"):
                self.meta[data["name"].lower()].append(data.get("content", ""))
            if data.get("property"):
                self.props[data["property"].lower()].append(data.get("content", ""))
        elif tag == "link":
            rel = set(data.get("rel", "").lower().split())
            if "canonical" in rel:
                self.canonical.append(data.get("href", ""))
            if "sitemap" in rel:
                self.sitemap.append(data.get("href", ""))
            if "alternate" in rel and data.get("hreflang"):
                self.hreflang[data["hreflang"].lower()] = data.get("href", "")
        elif tag == "script" and data.get("type", "").lower() == "application/ld+json":
            self._json = True
            self._chunks = []

    def handle_data(self, data: str) -> None:
        if self._json:
            self._chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._json:
            raw = "".join(self._chunks).strip()
            self._json = False
            self._chunks = []
            if raw:
                self.json_ld.append(json.loads(raw))


def walk_json(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def node_types(payloads: list[object]) -> Counter[str]:
    result: Counter[str] = Counter()
    for payload in payloads:
        for node in walk_json(payload):
            value = node.get("@type")
            if isinstance(value, str):
                result[value] += 1
            elif isinstance(value, list):
                result.update(item for item in value if isinstance(item, str))
    return result


def one(values: list[str], label: str, url: str) -> str:
    require(len(values) == 1, f"{label} count is {len(values)}: {url}")
    return values[0].strip()


def parse_page(raw: bytes, served_url: str, canonical_root: str, spec) -> set[str]:
    path, _, language, en_path, id_path, required_types = spec
    canonical_url = canonical_root + path
    page = Page()
    page.feed(raw.decode("utf-8"))

    require(page.lang == language, f"lang mismatch: {served_url}")
    require(page.h1 == 1, f"H1 count is {page.h1}: {served_url}")
    robots = one(page.meta.get("robots", []) + page.meta.get("googlebot", []), "robots meta", served_url)
    directives = {part.strip().lower() for part in robots.split(",") if part.strip()}
    require({"index", "follow"}.issubset(directives), f"not indexable: {served_url}")
    require(not {"noindex", "nofollow"} & directives, f"blocked robots directives: {served_url}")

    require(page.canonical == [canonical_url], f"canonical mismatch: {served_url} {page.canonical}")
    require(page.sitemap == [canonical_root + "sitemap.xml"], f"sitemap link mismatch: {served_url}")
    expected_hreflang = {
        "en": canonical_root + en_path,
        "id": canonical_root + id_path,
        "x-default": canonical_root + en_path,
    }
    require(page.hreflang == expected_hreflang, f"hreflang mismatch: {served_url} {page.hreflang}")
    require(one(page.props.get("og:url", []), "og:url", served_url) == canonical_url, f"og:url mismatch: {served_url}")

    social = one(page.props.get("og:image", []), "og:image", served_url)
    require(social == canonical_root + SOCIAL_PATH, f"og:image mismatch: {served_url}")
    require(one(page.meta.get("twitter:image", []), "twitter:image", served_url) == social, f"twitter:image mismatch: {served_url}")

    types = node_types(page.json_ld)
    require(required_types.issubset(types), f"schema {sorted(required_types)} missing: {served_url}; got {sorted(types)}")

    text = raw.decode("utf-8")
    if canonical_root == PRIMARY_ROOT:
        require(MIRROR_ROOT not in text, f"legacy GitHub SEO host remains in rendered page: {served_url}")
    return {social}


def verify_png(raw: bytes, label: str) -> None:
    require(len(raw) > 10_000, f"social PNG is unexpectedly small: {label}")
    require(raw[:8] == b"\x89PNG\r\n\x1a\n" and raw[12:16] == b"IHDR", f"invalid PNG: {label}")
    width, height, bit_depth, colour_type = struct.unpack(">IIBB", raw[16:26])
    require((width, height) == (1200, 630), f"social PNG is {width}x{height}: {label}")
    require(bit_depth == 8 and colour_type in {2, 6}, f"unexpected social PNG format: {label}")


def verify_release_payload(payload: dict, expected_version: str, label: str) -> None:
    require(payload.get("version") == expected_version, f"{label} version is {payload.get('version')!r}, expected {expected_version!r}")
    require(payload.get("schemaVersion", 0) >= 3, f"obsolete release manifest: {label}")
    require(payload.get("distributionEnabled") is True, f"distribution disabled: {label}")
    platforms = set(payload.get("platforms") or [])
    require({"windows-x64", "macos-universal"}.issubset(platforms), f"cross-platform release missing: {label} {sorted(platforms)}")
    expected_url = f"https://github.com/masarray/vst-enhancer/releases/tag/{expected_version}"
    require(payload.get("releaseUrl") == expected_url, f"releaseUrl/version mismatch: {label}")


def expected_urls(canonical_root: str) -> list[str]:
    return [canonical_root + spec[0] for spec in PAGE_SPECS]


def verify_discovery_text(robots: str, sitemap_xml: str, sitemap_txt: str, canonical_root: str, label: str) -> None:
    require("User-agent: *" in robots and "Allow: /" in robots, f"robots discovery missing: {label}")
    require("Disallow: /" not in robots, f"robots blocks crawling: {label}")
    require(f"Sitemap: {canonical_root}sitemap.xml" in robots, f"XML sitemap missing from robots: {label}")
    require(f"Sitemap: {canonical_root}sitemap.txt" in robots, f"text sitemap missing from robots: {label}")
    require(MIRROR_ROOT not in robots, f"mirror sitemap advertised by canonical artifact: {label}")

    tree = ElementTree.fromstring(sitemap_xml)
    require(tree.tag == f"{{{NS}}}urlset", f"bad sitemap root: {label}")
    locs = [item.findtext(f"{{{NS}}}loc", "").strip() for item in tree.findall(f"{{{NS}}}url")]
    expected = expected_urls(canonical_root)
    require(locs == expected and len(locs) == len(set(locs)), f"sitemap.xml URL mismatch: {label}")
    text_urls = [line.strip() for line in sitemap_txt.splitlines() if line.strip()]
    require(text_urls == expected, f"sitemap.txt URL mismatch: {label}")


def verify_headers_file(site_dir: Path, canonical_root: str) -> None:
    path = site_dir / "_headers"
    require(path.is_file(), "Cloudflare _headers file is missing")
    text = path.read_text(encoding="utf-8")
    for url in expected_urls(canonical_root):
        require(url in text, f"Cloudflare _headers lacks production rule for {url}")
        require(f"Link: <{url}>; rel=\"canonical\"" in text, f"Cloudflare Link canonical missing for {url}")
    require("X-Robots-Tag: index" not in text, "_headers must not override preview noindex with index")


def verify_static(site_dir: Path, expected_version: str, canonical_root: str) -> None:
    require(site_dir.is_dir(), f"static site does not exist: {site_dir}")
    social_urls: set[str] = set()
    for spec in PAGE_SPECS:
        rel_path = Path(spec[1]).relative_to("site")
        path = site_dir / rel_path
        require(path.is_file(), f"missing static page: {path}")
        social_urls.update(parse_page(path.read_bytes(), str(path), canonical_root, spec))

    verify_discovery_text(
        (site_dir / "robots.txt").read_text(encoding="utf-8"),
        (site_dir / "sitemap.xml").read_text(encoding="utf-8"),
        (site_dir / "sitemap.txt").read_text(encoding="utf-8"),
        canonical_root,
        str(site_dir),
    )
    payload = json.loads((site_dir / "release.json").read_text(encoding="utf-8"))
    verify_release_payload(payload, expected_version, str(site_dir / "release.json"))
    verify_png((site_dir / SOCIAL_PATH).read_bytes(), str(site_dir / SOCIAL_PATH))
    require((site_dir / VERIFY_PATH).is_file(), "Google verification file is missing")
    verify_headers_file(site_dir, canonical_root)
    require(social_urls == {canonical_root + SOCIAL_PATH}, "unexpected social image URL set")


def get(opener, url: str, accept: str = "text/html,*/*;q=0.8") -> tuple[dict[str, str], bytes]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ArSonKuPik-Canonical-SEO-Gate/4.0",
            "Accept": accept,
            "Cache-Control": "no-cache",
        },
    )
    with opener.open(request, timeout=25) as response:
        require(response.status == 200, f"{url} returned HTTP {response.status}")
        return {key.lower(): value for key, value in response.headers.items()}, response.read()


def verify_live_host(served_root: str, canonical_root: str, expected_version: str, primary: bool) -> None:
    opener = urllib.request.build_opener(NoRedirect())
    social_urls: set[str] = set()
    for spec in PAGE_SPECS:
        path = spec[0]
        served_url = served_root + path
        headers, raw = get(opener, served_url)
        x_robots = headers.get("x-robots-tag", "").lower()
        require("noindex" not in x_robots and "nofollow" not in x_robots, f"blocked X-Robots-Tag: {served_url}")
        social_urls.update(parse_page(raw, served_url, canonical_root, spec))
        if primary:
            link = headers.get("link", "")
            require(f"<{canonical_root + path}>; rel=\"canonical\"" in link, f"Cloudflare HTTP Link canonical missing: {served_url}")

    _, robots_raw = get(opener, served_root + "robots.txt", "text/plain,*/*;q=0.8")
    _, xml_raw = get(opener, served_root + "sitemap.xml", "application/xml,text/xml,*/*;q=0.8")
    _, txt_raw = get(opener, served_root + "sitemap.txt", "text/plain,*/*;q=0.8")
    verify_discovery_text(
        robots_raw.decode("utf-8"),
        xml_raw.decode("utf-8"),
        txt_raw.decode("utf-8"),
        canonical_root,
        served_root,
    )

    _, release_raw = get(opener, served_root + "release.json", "application/json,*/*;q=0.8")
    verify_release_payload(json.loads(release_raw.decode("utf-8")), expected_version, served_root + "release.json")
    _, social_raw = get(opener, canonical_root + SOCIAL_PATH, "image/png,*/*;q=0.8")
    verify_png(social_raw, canonical_root + SOCIAL_PATH)
    require(social_urls == {canonical_root + SOCIAL_PATH}, f"unexpected social URLs at {served_root}")

    if primary:
        get(opener, served_root + VERIFY_PATH, "text/plain,*/*;q=0.8")


def verify_index_normalization(primary_root: str) -> None:
    opener = urllib.request.build_opener(NoRedirect())
    for path in ("index.html", "id/index.html", "guide/index.html"):
        url = primary_root + path
        request = urllib.request.Request(url, headers={"User-Agent": "ArSonKuPik-Canonical-SEO-Gate/4.0"})
        try:
            opener.open(request, timeout=25)
        except urllib.error.HTTPError as exc:
            require(exc.code in {301, 308}, f"index normalization is not permanent for {url}: HTTP {exc.code}")
            expected = primary_root + path.removesuffix("index.html")
            actual = urllib.parse.urljoin(url, exc.headers.get("location", ""))
            require(actual == expected, f"index normalization mismatch: {url} -> {actual}, expected {expected}")
        else:
            raise AssertionError(f"index.html did not redirect: {url}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--static-dir")
    parser.add_argument("--primary-root", default=PRIMARY_ROOT)
    parser.add_argument("--mirror-root", default=MIRROR_ROOT)
    parser.add_argument("--skip-mirror", action="store_true")
    parser.add_argument("--attempts", type=int, default=30)
    parser.add_argument("--delay-seconds", type=float, default=10.0)
    args = parser.parse_args()

    primary_root = root(args.primary_root)
    mirror_root = root(args.mirror_root)

    if args.static_dir:
        verify_static(Path(args.static_dir).resolve(), args.expected_version, primary_root)
        print("[PASS] Rendered static artifact has Cloudflare canonical SEO identity and protected preview-header policy.")
        return 0

    last_error: Exception | None = None
    for attempt in range(1, args.attempts + 1):
        try:
            verify_live_host(primary_root, primary_root, args.expected_version, primary=True)
            verify_index_normalization(primary_root)
            if not args.skip_mirror:
                verify_live_host(mirror_root, primary_root, args.expected_version, primary=False)
        except (
            AssertionError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            ElementTree.ParseError,
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            struct.error,
        ) as exc:
            last_error = exc
            if attempt == args.attempts:
                break
            print(f"[WAIT] Canonical SEO verification attempt {attempt}/{args.attempts} did not pass yet: {exc}")
            time.sleep(args.delay_seconds)
            continue
        target = "Cloudflare primary and GitHub Pages mirror" if not args.skip_mirror else "Cloudflare primary"
        print(f"[PASS] {target} serve 14 pages with Cloudflare canonical, hreflang, schema, sitemap, social-image and release contracts.")
        return 0

    print(f"[FAIL] Canonical SEO verification did not converge: {last_error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
