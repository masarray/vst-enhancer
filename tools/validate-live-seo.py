#!/usr/bin/env python3
"""Verify that the deployed GitHub Pages site serves the canonical SEO contract."""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from xml.etree import ElementTree

ROOT = "https://masarray.github.io/vst-enhancer/"
URLS = [
    ROOT,
    ROOT + "id/",
    ROOT + "guide/",
    ROOT + "id/guide/",
    ROOT + "activation/",
    ROOT + "id/activation/",
]
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, "Unexpected redirect", headers, fp)


class SeoHead(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.robots: list[str] = []
        self.canonical: list[str] = []
        self.h1 = 0

    def handle_starttag(self, tag, attrs) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag == "h1":
            self.h1 += 1
        elif tag == "meta" and data.get("name", "").lower() in {"robots", "googlebot"}:
            self.robots.append(data.get("content", ""))
        elif tag == "link" and "canonical" in data.get("rel", "").lower().split():
            self.canonical.append(data.get("href", ""))


def get(opener, url: str) -> tuple[dict[str, str], bytes]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ArSonKuPik-SEO-Release-Gate/1.0",
            "Accept": "text/html,application/xml,text/plain,application/json;q=0.9,*/*;q=0.8",
            "Cache-Control": "no-cache",
        },
    )
    with opener.open(request, timeout=25) as response:
        if response.status != 200:
            raise AssertionError(f"{url} returned HTTP {response.status}")
        headers = {key.lower(): value for key, value in response.headers.items()}
        return headers, response.read()


def verify_pages(opener) -> None:
    for url in URLS:
        headers, raw = get(opener, url)
        x_robots = headers.get("x-robots-tag", "").lower()
        if "noindex" in x_robots:
            raise AssertionError(f"{url} returned X-Robots-Tag noindex")

        text = raw.decode("utf-8")
        page = SeoHead()
        page.feed(text)
        if page.canonical != [url]:
            raise AssertionError(f"{url} canonical mismatch: {page.canonical}")
        if len(page.robots) != 1:
            raise AssertionError(f"{url} robots meta count is {len(page.robots)}")
        directives = {
            value.strip().lower()
            for value in page.robots[0].split(",")
            if value.strip()
        }
        if not {"index", "follow"}.issubset(directives):
            raise AssertionError(f"{url} lacks index,follow: {sorted(directives)}")
        if "noindex" in directives or "nofollow" in directives:
            raise AssertionError(f"{url} is blocked: {sorted(directives)}")
        if page.h1 != 1:
            raise AssertionError(f"{url} has {page.h1} H1 elements")


def verify_discovery(opener) -> None:
    _, robots_raw = get(opener, ROOT + "robots.txt")
    robots = robots_raw.decode("utf-8")
    if f"Sitemap: {ROOT}sitemap.xml" not in robots:
        raise AssertionError("robots.txt does not advertise sitemap.xml")

    _, sitemap_raw = get(opener, ROOT + "sitemap.xml")
    tree = ElementTree.fromstring(sitemap_raw.decode("utf-8"))
    if tree.tag != f"{{{NS}}}urlset":
        raise AssertionError(f"Unexpected sitemap root: {tree.tag}")
    locs = [
        node.findtext(f"{{{NS}}}loc", "").strip()
        for node in tree.findall(f"{{{NS}}}url")
    ]
    if locs != URLS:
        raise AssertionError(f"Live sitemap URL mismatch: {locs}")

    _, text_raw = get(opener, ROOT + "sitemap.txt")
    text_urls = [
        line.strip()
        for line in text_raw.decode("utf-8").splitlines()
        if line.strip()
    ]
    if text_urls != URLS:
        raise AssertionError(f"Live text sitemap URL mismatch: {text_urls}")


def verify_release(opener, expected_version: str) -> None:
    _, raw = get(opener, ROOT + "release.json")
    payload = json.loads(raw.decode("utf-8"))
    if payload.get("version") != expected_version:
        raise AssertionError(
            f"Live release version is {payload.get('version')!r}, expected {expected_version!r}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--attempts", type=int, default=18)
    parser.add_argument("--delay-seconds", type=float, default=10.0)
    args = parser.parse_args()

    opener = urllib.request.build_opener(NoRedirect())
    last_error: Exception | None = None

    for attempt in range(1, args.attempts + 1):
        try:
            verify_pages(opener)
            verify_discovery(opener)
            verify_release(opener, args.expected_version)
        except (
            AssertionError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            ElementTree.ParseError,
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
        ) as exc:
            last_error = exc
            if attempt == args.attempts:
                break
            print(
                f"[WAIT] Live SEO verification attempt {attempt}/{args.attempts} "
                f"did not pass yet: {exc}"
            )
            time.sleep(args.delay_seconds)
            continue

        print(
            "[PASS] Live GitHub Pages serves six non-redirecting canonical pages, "
            "indexable robots directives and both complete sitemap formats."
        )
        return 0

    print(f"[FAIL] Live SEO verification did not converge: {last_error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
