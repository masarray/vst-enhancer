#!/usr/bin/env python3
"""Validate deployed ArSonKuPik SEO endpoints after GitHub Pages propagation."""
from __future__ import annotations
import argparse, time, urllib.request, urllib.error, sys
from html.parser import HTMLParser
from xml.etree import ElementTree
ROOT='https://masarray.github.io/vst-enhancer/'
URLS=['https://masarray.github.io/vst-enhancer/', 'https://masarray.github.io/vst-enhancer/id/', 'https://masarray.github.io/vst-enhancer/guide/', 'https://masarray.github.io/vst-enhancer/id/guide/', 'https://masarray.github.io/vst-enhancer/activation/', 'https://masarray.github.io/vst-enhancer/id/activation/', 'https://masarray.github.io/vst-enhancer/about/', 'https://masarray.github.io/vst-enhancer/id/about/', 'https://masarray.github.io/vst-enhancer/measurements/', 'https://masarray.github.io/vst-enhancer/id/measurements/', 'https://masarray.github.io/vst-enhancer/audio-comparisons/', 'https://masarray.github.io/vst-enhancer/id/audio-comparisons/', 'https://masarray.github.io/vst-enhancer/use-cases/windows-system-audio/', 'https://masarray.github.io/vst-enhancer/id/use-cases/windows-system-audio/']
NS="http://www.sitemaps.org/schemas/sitemap/0.9"
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): return None
class P(HTMLParser):
    def __init__(self): super().__init__(); self.canonical=[]; self.robots=""; self.h1=0
    def handle_starttag(self,t,a):
        d={k.lower():v or "" for k,v in a}
        if t=="h1": self.h1+=1
        elif t=="meta" and d.get("name","").lower()=="robots": self.robots=d.get("content","").lower()
        elif t=="link" and "canonical" in d.get("rel","").lower().split(): self.canonical.append(d.get("href",""))
def get(opener,url):
    req=urllib.request.Request(url,headers={"User-Agent":"ArSonKuPik-SEO-Validator/2.0","Cache-Control":"no-cache"})
    with opener.open(req,timeout=25) as r: return r.status,dict(r.headers),r.read()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--attempts",type=int,default=12); ap.add_argument("--delay",type=float,default=10); ap.add_argument("--expected-version"); args=ap.parse_args(); opener=urllib.request.build_opener(NoRedirect)
    last=None
    for attempt in range(1,args.attempts+1):
        try:
            for url in URLS:
                status,headers,raw=get(opener,url)
                if status!=200: raise AssertionError(f"{url} status {status}")
                if "noindex" in headers.get("X-Robots-Tag","").lower(): raise AssertionError(f"X-Robots noindex: {url}")
                p=P(); p.feed(raw.decode("utf-8"));
                if p.canonical!=[url] or "index" not in p.robots or "noindex" in p.robots or p.h1!=1: raise AssertionError(f"page signals: {url}")
            _,_,raw=get(opener,ROOT+"sitemap.xml"); tree=ElementTree.fromstring(raw.decode("utf-8")); locs=[n.findtext(f"{{{NS}}}loc","").strip() for n in tree.findall(f"{{{NS}}}url")]
            if locs!=URLS: raise AssertionError("live sitemap mismatch")
            print(f"[PASS] Live SEO validation passed for {len(URLS)} pages."); return
        except Exception as e:
            last=e
            if attempt<args.attempts: time.sleep(args.delay)
    raise SystemExit(f"[FAIL] Live SEO validation: {last}")
if __name__=="__main__": main()
