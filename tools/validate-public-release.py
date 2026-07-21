#!/usr/bin/env python3
"""Validate ArSonKuPik release integrity, localized pages and V4 runtime."""
from __future__ import annotations

import argparse, json, re, sys, urllib.error, urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree

ROOT_URL = "https://masarray.github.io/vst-enhancer/"
ID_URL = ROOT_URL + "id/"
RELEASE_ROOT = "https://github.com/masarray/vst-enhancer/releases"
ASSET_ROOT = RELEASE_ROOT + "/download/"
VERSION_RE = re.compile(r"^v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.is_file(), f"Missing file: {path.as_posix()}")
    text = path.read_text(encoding="utf-8")
    require(bool(text.strip()), f"Empty file: {path.as_posix()}")
    return text


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.lang=""; self.title=""; self.description=""; self.canonical=""; self.hreflang={}; self.ids=set(); self.h1=""; self.scripts={}; self._title=False; self._h1=False; self._sid=None; self._chunks=[]
    def handle_starttag(self, tag, attrs):
        data={k:v or "" for k,v in attrs}
        if tag=="html": self.lang=data.get("lang","")
        if tag=="title": self._title=True
        if tag=="h1": self._h1=True
        if data.get("id"): self.ids.add(data["id"])
        if tag=="meta" and data.get("name")=="description": self.description=data.get("content","")
        if tag=="link":
            rel=data.get("rel","").split()
            if "canonical" in rel: self.canonical=data.get("href","")
            if "alternate" in rel and data.get("hreflang"): self.hreflang[data["hreflang"]]=data.get("href","")
        if tag=="script" and data.get("id"): self._sid=data["id"]; self._chunks=[]
    def handle_data(self, data):
        if self._title: self.title += data
        if self._h1: self.h1 += data
        if self._sid: self._chunks.append(data)
    def handle_endtag(self, tag):
        if tag=="title": self._title=False
        if tag=="h1": self._h1=False
        if tag=="script" and self._sid:
            self.scripts[self._sid]="".join(self._chunks); self._sid=None; self._chunks=[]


def page(text: str) -> Page:
    result=Page(); result.feed(text); return result


def validate_release(root: Path) -> dict:
    release=json.loads(read(root/"site/release.json")); localized=json.loads(read(root/"site/id/release.json"))
    require(release==localized, "Localized release manifest drift")
    required={"schemaVersion","version","distributionEnabled","evaluationDays","purchaseCheckoutAvailable","releaseUrl","installerUrl","vst3Url","standaloneUrl","checksumsUrl","unsigned","signatureStatus"}
    require(not required.difference(release), f"release.json missing {sorted(required.difference(release))}")
    require(VERSION_RE.fullmatch(str(release["version"])) is not None, "Invalid version")
    require(release["schemaVersion"]>=2 and release["distributionEnabled"] is True, "Release schema/status invalid")
    require(release["automaticCharge"] is False and release["subscription"] is False and release["purchaseObligation"] is False, "No-pressure licence flags changed")
    require(release["purchaseCheckoutAvailable"] is False and "purchaseUrl" not in release, "Checkout published before configuration")
    version=str(release["version"])
    require(str(release["releaseUrl"]).startswith(RELEASE_ROOT) and str(release["releaseUrl"]).endswith("/tag/"+version), "Release URL mismatch")
    endings={"installerUrl":f"ArSonKuPik-{version}-Windows-x64-Setup.exe","vst3Url":f"ArSonKuPik-{version}-Windows-x64-VST3.zip","standaloneUrl":f"ArSonKuPik-{version}-Windows-x64-Standalone.zip","checksumsUrl":"SHA256SUMS.txt"}
    for key, ending in endings.items():
        value=str(release[key]); parsed=urlparse(value)
        require(value.startswith(ASSET_ROOT) and parsed.scheme=="https" and parsed.hostname=="github.com" and value.endswith("/"+ending), f"{key} invalid")
    return release


def validate_page(text: str, language: str, canonical: str, version: str, static_hreflang: bool) -> None:
    p=page(text); require(p.lang==language, f"{canonical} lang mismatch"); require(p.canonical==canonical, f"{canonical} canonical mismatch")
    require("ArSonKuPik" in p.title and "VST3" in p.title and "365" not in p.title, f"{canonical} title is not product-first")
    require(80<=len(p.description)<=180 and "365" not in p.description, f"{canonical} description is not product-first")
    require("Suara lebih berisi" in p.h1 if language=="id" else "Fuller, clearer" in p.h1, f"{canonical} H1 not localized")
    require("software-structured-data" in p.scripts, f"{canonical} missing JSON-LD")
    graph=json.loads(p.scripts["software-structured-data"])["@graph"]; software=next(x for x in graph if x.get("@type")=="SoftwareApplication")
    schema_language=software.get("inLanguage"); language_ok=schema_language==language or (language=="en" and schema_language==["en","id"])
    require(software.get("softwareVersion")==version.lstrip("v") and software.get("url")==canonical and language_ok, f"{canonical} structured data mismatch")
    for item in ("main","workflow","features","presets","download","faq"): require(item in p.ids, f"{canonical} missing #{item}")
    require("for-you" in p.ids or "sound" in p.ids, f"{canonical} missing flagship sound section")
    if static_hreflang: require(p.hreflang=={"en":ROOT_URL,"id":ID_URL,"x-default":ROOT_URL}, "Indonesian hreflang mismatch")


def validate_sitemap(root: Path) -> None:
    tree=ElementTree.fromstring(read(root/"site/sitemap.xml")); ns={"s":"http://www.sitemaps.org/schemas/sitemap/0.9","x":"http://www.w3.org/1999/xhtml"}; urls=tree.findall("s:url",ns)
    require([u.findtext("s:loc",default="",namespaces=ns) for u in urls]==[ROOT_URL,ID_URL], "Sitemap localized URLs mismatch")
    expected={"en":ROOT_URL,"id":ID_URL,"x-default":ROOT_URL}
    for u in urls: require({x.attrib.get("hreflang"):x.attrib.get("href") for x in u.findall("x:link",ns)}==expected, "Sitemap hreflang mismatch")


def validate_runtime(root: Path) -> None:
    app=read(root/"site/app.js"); trial=read(root/"site/trial-page.js"); experience=read(root/"site/experience-v4.js"); styles=read(root/"site/experience-v4.css")
    for token in ("ID_URL","window.location.assign","ensureAlternate('en'","ensureAlternate('id'","latest-release.js","IntersectionObserver","stopImmediatePropagation","askp:release-ready"):
        require(token in trial, f"Stable locale runtime missing {token}")
    require("experience-v4.js" in trial and "v4-audio-motion" in trial, "V4 experience is not loaded")
    for token in ("setupProductPreview","setupPresetExplorer","preset-explorer-ready","preset-browser","setupScrollReveals","setupNavigationState","setupPointerDepth","prefers-reduced-motion"):
        require(token in experience, f"V4 runtime missing {token}")
    for selector in (".product-preview-dialog",".preset-universe.preset-explorer-ready",".preset-browser",".preset-toolbar",".motion-ready [data-reveal]",".landing-nav.is-scrolled"):
        require(selector in styles, f"V4 styles missing {selector}")
    require("browser.append(toolbar, groupsContainer)" in experience, "Preset browser DOM contract missing")
    require("minmax(0, 1.32fr)" in styles, "Preset browser desktop grid contract missing")
    require("@media (prefers-reduced-motion: reduce)" in styles, "Reduced-motion safety missing")
    require("premium-polish.css" not in trial and "landing-v2.css" not in trial, "Core visual CSS must remain static")
    require("fetch('./release.json'" in app, "Release controller must retain its reviewed local manifest request")


def remote_check(urls: list[str]) -> None:
    for url in urls:
        req=urllib.request.Request(url,method="HEAD",headers={"User-Agent":"ArSonKuPik-validator/4.0"})
        try:
            with urllib.request.urlopen(req,timeout=20) as response: require(200<=response.status<400, f"Remote status {response.status}: {url}")
        except (urllib.error.HTTPError,urllib.error.URLError) as exc: raise AssertionError(f"Remote URL failed: {url} ({exc})") from exc


def main() -> int:
    args_parser=argparse.ArgumentParser(description=__doc__); args_parser.add_argument("--check-remote",action="store_true"); args_parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]); args=args_parser.parse_args(); root=args_parser.parse_args().root.resolve()
    try:
        release=validate_release(root)
        validate_page(read(root/"site/index.html"),"en",ROOT_URL,str(release["version"]),False)
        validate_page(read(root/"site/id/index.html"),"id",ID_URL,str(release["version"]),True)
        validate_sitemap(root); validate_runtime(root)
        if args.check_remote: remote_check([str(release[k]) for k in ("releaseUrl","installerUrl","vst3Url","standaloneUrl","checksumsUrl")])
    except (AssertionError,json.JSONDecodeError,ElementTree.ParseError,StopIteration,ValueError) as exc:
        print(f"VALIDATION FAILED: {exc}",file=sys.stderr); return 1
    print(f"Validation passed: product-first EN/ID pages, stable V4 preset layout, audio motion and release {release['version']}."); return 0

if __name__=="__main__": raise SystemExit(main())
