#!/usr/bin/env python3
"""Validate all public ArSonKuPik SEO pages."""
from __future__ import annotations
import json, re, sys
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree
ROOT='https://masarray.github.io/vst-enhancer/'
SOCIAL='https://masarray.github.io/vst-enhancer/assets/arsonkupik-guide-social-1200x630.png'
SPECS=[('https://masarray.github.io/vst-enhancer/', 'site/index.html', 'en', 'https://masarray.github.io/vst-enhancer/', 'https://masarray.github.io/vst-enhancer/id/', ['WebSite', 'WebPage', 'SoftwareApplication']), ('https://masarray.github.io/vst-enhancer/id/', 'site/id/index.html', 'id', 'https://masarray.github.io/vst-enhancer/', 'https://masarray.github.io/vst-enhancer/id/', ['WebPage', 'SoftwareApplication']), ('https://masarray.github.io/vst-enhancer/guide/', 'site/guide/index.html', 'en', 'https://masarray.github.io/vst-enhancer/guide/', 'https://masarray.github.io/vst-enhancer/id/guide/', ['TechArticle', 'BreadcrumbList']), ('https://masarray.github.io/vst-enhancer/id/guide/', 'site/id/guide/index.html', 'id', 'https://masarray.github.io/vst-enhancer/guide/', 'https://masarray.github.io/vst-enhancer/id/guide/', ['TechArticle', 'BreadcrumbList']), ('https://masarray.github.io/vst-enhancer/activation/', 'site/activation/index.html', 'en', 'https://masarray.github.io/vst-enhancer/activation/', 'https://masarray.github.io/vst-enhancer/id/activation/', ['WebPage']), ('https://masarray.github.io/vst-enhancer/id/activation/', 'site/id/activation/index.html', 'id', 'https://masarray.github.io/vst-enhancer/activation/', 'https://masarray.github.io/vst-enhancer/id/activation/', ['WebPage']), ('https://masarray.github.io/vst-enhancer/about/', 'site/about/index.html', 'en', 'https://masarray.github.io/vst-enhancer/about/', 'https://masarray.github.io/vst-enhancer/id/about/', ['AboutPage', 'BreadcrumbList']), ('https://masarray.github.io/vst-enhancer/id/about/', 'site/id/about/index.html', 'id', 'https://masarray.github.io/vst-enhancer/about/', 'https://masarray.github.io/vst-enhancer/id/about/', ['AboutPage', 'BreadcrumbList']), ('https://masarray.github.io/vst-enhancer/measurements/', 'site/measurements/index.html', 'en', 'https://masarray.github.io/vst-enhancer/measurements/', 'https://masarray.github.io/vst-enhancer/id/measurements/', ['TechArticle', 'BreadcrumbList']), ('https://masarray.github.io/vst-enhancer/id/measurements/', 'site/id/measurements/index.html', 'id', 'https://masarray.github.io/vst-enhancer/measurements/', 'https://masarray.github.io/vst-enhancer/id/measurements/', ['TechArticle', 'BreadcrumbList']), ('https://masarray.github.io/vst-enhancer/audio-comparisons/', 'site/audio-comparisons/index.html', 'en', 'https://masarray.github.io/vst-enhancer/audio-comparisons/', 'https://masarray.github.io/vst-enhancer/id/audio-comparisons/', ['TechArticle', 'BreadcrumbList']), ('https://masarray.github.io/vst-enhancer/id/audio-comparisons/', 'site/id/audio-comparisons/index.html', 'id', 'https://masarray.github.io/vst-enhancer/audio-comparisons/', 'https://masarray.github.io/vst-enhancer/id/audio-comparisons/', ['TechArticle', 'BreadcrumbList']), ('https://masarray.github.io/vst-enhancer/use-cases/windows-system-audio/', 'site/use-cases/windows-system-audio/index.html', 'en', 'https://masarray.github.io/vst-enhancer/use-cases/windows-system-audio/', 'https://masarray.github.io/vst-enhancer/id/use-cases/windows-system-audio/', ['TechArticle', 'BreadcrumbList']), ('https://masarray.github.io/vst-enhancer/id/use-cases/windows-system-audio/', 'site/id/use-cases/windows-system-audio/index.html', 'id', 'https://masarray.github.io/vst-enhancer/use-cases/windows-system-audio/', 'https://masarray.github.io/vst-enhancer/id/use-cases/windows-system-audio/', ['TechArticle', 'BreadcrumbList'])]
NS="http://www.sitemaps.org/schemas/sitemap/0.9"
class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.lang=""; self.title=""; self._title=False; self.h1=0; self.meta={}; self.props={}; self.canonical=[]; self.sitemap=[]; self.hreflang={}; self.jsonld=[]; self._json=False; self._chunks=[]; self.refresh=False
    def handle_starttag(self,tag,attrs):
        d={k.lower():v or "" for k,v in attrs}
        if tag=="html": self.lang=d.get("lang","").lower()
        elif tag=="title": self._title=True
        elif tag=="h1": self.h1+=1
        elif tag=="meta":
            if d.get("http-equiv","").lower()=="refresh": self.refresh=True
            if d.get("name"): self.meta[d["name"].lower()]=d.get("content","")
            if d.get("property"): self.props[d["property"].lower()]=d.get("content","")
        elif tag=="link":
            rel=set(d.get("rel","").lower().split())
            if "canonical" in rel: self.canonical.append(d.get("href",""))
            if "sitemap" in rel: self.sitemap.append(d.get("href",""))
            if "alternate" in rel and d.get("hreflang"): self.hreflang[d["hreflang"].lower()]=d.get("href","")
        elif tag=="script" and d.get("type","").lower()=="application/ld+json": self._json=True; self._chunks=[]
    def handle_data(self,data):
        if self._title: self.title+=data
        if self._json: self._chunks.append(data)
    def handle_endtag(self,tag):
        if tag=="title": self._title=False
        elif tag=="script" and self._json:
            raw="".join(self._chunks).strip(); self._json=False
            if raw: self.jsonld.append(json.loads(raw))
def types(payload):
    found=set()
    def walk(x):
        if isinstance(x,dict):
            t=x.get("@type")
            if isinstance(t,str): found.add(t)
            elif isinstance(t,list): found.update(v for v in t if isinstance(v,str))
            for v in x.values(): walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
    walk(payload); return found
def check(ok,msg):
    if not ok: raise AssertionError(msg)
def main():
    base=Path(__file__).resolve().parents[1]
    expected=[]
    for url,rel,lang,en_url,id_url,required in SPECS:
        expected.append(url); raw=(base/rel).read_bytes(); check(not raw.startswith(b"\xef\xbb\xbf"),f"BOM: {rel}")
        p=P(); p.feed(raw.decode("utf-8")); check(p.lang==lang,f"lang: {url}"); check(30<=len(p.title.strip())<=78,f"title: {url}"); check(70<=len(p.meta.get("description", ""))<=230,f"description: {url}"); check(p.h1==1 and not p.refresh,f"H1/refresh: {url}")
        robots={x.strip().lower() for x in p.meta.get("robots","").split(",")}; check({"index","follow"}<=robots and "noindex" not in robots,f"robots: {url}")
        check(p.canonical==[url],f"canonical: {url}"); check(p.sitemap==[ROOT+"sitemap.xml"],f"sitemap link: {url}"); check(p.hreflang=={"en":en_url,"id":id_url,"x-default":en_url},f"hreflang: {url}")
        check(p.props.get("og:url")==url and p.props.get("og:image")==SOCIAL,f"OG URL/image: {url}"); check(p.props.get("og:image:width")=="1200" and p.props.get("og:image:height")=="630",f"OG dimensions: {url}")
        for key in ("og:title","og:description","og:image:alt"): check(bool(p.props.get(key)),f"missing {key}: {url}")
        check(p.meta.get("twitter:card")=="summary_large_image" and p.meta.get("twitter:image")==SOCIAL,f"Twitter: {url}")
        for key in ("twitter:title","twitter:description","twitter:image:alt"): check(bool(p.meta.get(key)),f"missing {key}: {url}")
        all_types=set(); [all_types.update(types(x)) for x in p.jsonld]
        check(set(required)<=all_types,f"schema {required} missing at {url}; got {sorted(all_types)}")
    tree=ElementTree.parse(base/"site/sitemap.xml").getroot(); locs=[n.findtext(f"{{{NS}}}loc","").strip() for n in tree.findall(f"{{{NS}}}url")]
    check(locs==expected and len(locs)==len(set(locs)),"sitemap.xml mismatch"); txt=[x.strip() for x in (base/"site/sitemap.txt").read_text().splitlines() if x.strip()]; check(txt==expected,"sitemap.txt mismatch")
    img=base/"site/assets/arsonkupik-guide-social-1200x630.png"; check(img.exists() and img.stat().st_size>10000,"social PNG missing")
    print(f"[PASS] {len(expected)} canonical pages: metadata, social image, schema, hreflang and sitemaps are consistent.")
if __name__=="__main__":
    try: main()
    except Exception as e: print(f"[FAIL] SEO validation: {e}"); sys.exit(1)
