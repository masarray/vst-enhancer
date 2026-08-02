#!/usr/bin/env python3
"""Apply ArSonKuPik Search Console P1 + P2 improvements to a local repo.

Run from the repository root after extracting this bundle into it:
    python apply_seo_p1_p2.py

The script is idempotent and creates .seo-backup copies before overwriting files.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path
from xml.etree import ElementTree

ROOT_URL = "https://masarray.github.io/vst-enhancer/"
TODAY = "2026-08-02"
SOCIAL_URL = ROOT_URL + "assets/arsonkupik-guide-social-1200x630.png"
MARK_HEAD_BEGIN = "<!-- SEO-P1-HEAD-BEGIN -->"
MARK_HEAD_END = "<!-- SEO-P1-HEAD-END -->"
MARK_SCHEMA_BEGIN = "<!-- SEO-P1-SCHEMA-BEGIN -->"
MARK_SCHEMA_END = "<!-- SEO-P1-SCHEMA-END -->"
MARK_HUB_BEGIN = "<!-- SEO-P2-HUB-BEGIN -->"
MARK_HUB_END = "<!-- SEO-P2-HUB-END -->"

REPO = Path.cwd()
SITE = REPO / "site"
TOOLS = REPO / "tools"


def fail(message: str) -> None:
    raise SystemExit(f"[FAIL] {message}")


def require_repo() -> None:
    required = [
        SITE / "index.html",
        SITE / "id/index.html",
        SITE / "guide/index.html",
        SITE / "id/guide/index.html",
        SITE / "activation/index.html",
        SITE / "id/activation/index.html",
        SITE / "sitemap.xml",
        SITE / "sitemap.txt",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        fail("Run from the vst-enhancer repository root. Missing: " + ", ".join(missing))


def ignore_backup_dir() -> None:
    exclude = REPO / ".git/info/exclude"
    if not exclude.exists():
        return
    rule = ".seo-backup/"
    current = exclude.read_text(encoding="utf-8", errors="ignore")
    if rule not in {line.strip() for line in current.splitlines()}:
        with exclude.open("a", encoding="utf-8", newline="\n") as handle:
            if current and not current.endswith("\n"):
                handle.write("\n")
            handle.write(rule + "\n")

def backup(path: Path) -> None:
    if not path.exists():
        return
    try:
        relative = path.resolve().relative_to(REPO.resolve())
    except ValueError:
        fail(f"Refusing to back up a path outside the repository: {path}")
    backup_path = REPO / ".seo-backup" / relative
    if not backup_path.exists():
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    backup(path)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"[WRITE] {path.relative_to(REPO)}")


def remove_marked(text: str, begin: str, end: str) -> str:
    return re.sub(
        rf"\n?\s*{re.escape(begin)}.*?{re.escape(end)}\s*\n?",
        "\n",
        text,
        flags=re.S,
    )


def set_title(text: str, value: str) -> str:
    new, n = re.subn(r"<title>.*?</title>", f"<title>{escape(value)}</title>", text, count=1, flags=re.S)
    if n != 1:
        fail("Could not find exactly one <title>")
    return new


def set_meta_name(text: str, name: str, content: str) -> str:
    pattern = rf'<meta\s+name=["\']{re.escape(name)}["\']\s+content=["\'].*?["\']\s*/?>'
    replacement = f'<meta name="{name}" content="{escape(content, quote=True)}">'
    new, n = re.subn(pattern, replacement, text, count=1, flags=re.I | re.S)
    if n == 0:
        marker = "  <meta name=\"theme-color\""
        pos = new.find(marker)
        if pos < 0:
            pos = new.find("</head>")
        new = new[:pos] + "  " + replacement + "\n" + new[pos:]
    return new


def set_meta_property(text: str, prop: str, content: str) -> str:
    pattern = rf'<meta\s+property=["\']{re.escape(prop)}["\']\s+content=["\'].*?["\']\s*/?>'
    replacement = f'<meta property="{prop}" content="{escape(content, quote=True)}">'
    new, n = re.subn(pattern, replacement, text, count=1, flags=re.I | re.S)
    if n == 0:
        marker = "</head>"
        new = new.replace(marker, "  " + replacement + "\n" + marker, 1)
    return new


def ensure_stylesheet(text: str, href: str) -> str:
    if f'href="{href}"' in text:
        return text
    marker = "</head>"
    return text.replace(marker, f'  <link rel="stylesheet" href="{href}">\n{marker}', 1)


def ensure_sitemap_link(text: str) -> str:
    if 'rel="sitemap"' in text:
        return text
    marker = re.search(r'\s*<link rel="icon"', text)
    line = f'  <link rel="sitemap" type="application/xml" href="{ROOT_URL}sitemap.xml">\n'
    if marker:
        return text[: marker.start()] + "\n" + line + text[marker.start():]
    return text.replace("</head>", line + "</head>", 1)


def insert_before(text: str, marker: str, block: str) -> str:
    if marker not in text:
        fail(f"Insertion marker not found: {marker}")
    return text.replace(marker, block.rstrip() + "\n\n" + marker, 1)


def add_head_block(text: str, *, lang: str, canonical: str, title: str, description: str, og_type: str = "website") -> str:
    text = remove_marked(text, MARK_HEAD_BEGIN, MARK_HEAD_END)
    alt = "Tampilan dan panduan ArSonKuPik VST3 audio enhancer" if lang == "id" else "ArSonKuPik VST3 audio enhancer interface and guide"
    locale = "id_ID" if lang == "id" else "en_US"
    alt_locale = "en_US" if lang == "id" else "id_ID"
    block = f"""
  {MARK_HEAD_BEGIN}
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="ArSonKuPik">
  <meta property="og:locale" content="{locale}">
  <meta property="og:locale:alternate" content="{alt_locale}">
  <meta property="og:title" content="{escape(title, quote=True)}">
  <meta property="og:description" content="{escape(description, quote=True)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SOCIAL_URL}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{alt}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escape(title, quote=True)}">
  <meta name="twitter:description" content="{escape(description, quote=True)}">
  <meta name="twitter:image" content="{SOCIAL_URL}">
  <meta name="twitter:image:alt" content="{alt}">
  {MARK_HEAD_END}
"""
    # Remove old OG/Twitter tags so each key is unique.
    text = re.sub(r'\s*<meta\s+(?:property="og:[^"]+"|name="twitter:[^"]+")\s+content="[^"]*"\s*/?>', "", text, flags=re.I)
    text = ensure_sitemap_link(text)
    return text.replace("</head>", block.rstrip() + "\n</head>", 1)


def replace_jsonld_scripts(text: str, transform) -> str:
    pattern = re.compile(r'(<script[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)', re.I | re.S)
    matches = list(pattern.finditer(text))
    if not matches:
        return text
    out = []
    cursor = 0
    for match in matches:
        out.append(text[cursor:match.start()])
        raw = match.group(2).strip()
        try:
            payload = json.loads(raw)
            payload = transform(payload)
            rendered = json.dumps(payload, ensure_ascii=False, indent=2)
            out.append(match.group(1) + "\n" + rendered + "\n  " + match.group(3))
        except json.JSONDecodeError:
            out.append(match.group(0))
        cursor = match.end()
    out.append(text[cursor:])
    return "".join(out)


def ensure_home_schema(text: str, lang: str, canonical: str, page_title: str) -> str:
    def transform(payload):
        if not isinstance(payload, dict):
            return payload
        graph = payload.get("@graph")
        if not isinstance(graph, list):
            return payload
        cleaned = []
        for node in graph:
            if not isinstance(node, dict):
                cleaned.append(node)
                continue
            if lang == "id" and node.get("@type") == "WebSite":
                continue
            if isinstance(node.get("isPartOf"), dict) and node["isPartOf"].get("@id", "").endswith("/id/#website"):
                node["isPartOf"] = {"@id": ROOT_URL + "#website"}
            if node.get("@type") == "SoftwareApplication":
                node["mainEntityOfPage"] = {"@id": canonical + "#webpage"}
            if lang == "en" and node.get("@type") == "WebSite":
                node["@id"] = ROOT_URL + "#website"
                node["url"] = ROOT_URL
                node["name"] = "ArSonKuPik"
                node["alternateName"] = ["ArSonKuPik VST", "Mas Ari Audio Enhancer"]
            cleaned.append(node)
        if not any(isinstance(n, dict) and n.get("@id") == canonical + "#webpage" for n in cleaned):
            cleaned.insert(1 if lang == "en" else 0, {
                "@type": "WebPage",
                "@id": canonical + "#webpage",
                "url": canonical,
                "name": page_title,
                "inLanguage": lang,
                "isPartOf": {"@id": ROOT_URL + "#website"},
                "primaryImageOfPage": SOCIAL_URL,
            })
        payload["@graph"] = cleaned
        return payload
    return replace_jsonld_scripts(text, transform)


def ensure_activation_schema(text: str, lang: str, canonical: str, title: str, description: str) -> str:
    existing_types: set[str] = set()
    pattern = re.compile(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)(?:</script>)', re.I | re.S)

    def collect_types(value) -> None:
        if isinstance(value, dict):
            kind = value.get("@type")
            if isinstance(kind, str):
                existing_types.add(kind)
            elif isinstance(kind, list):
                existing_types.update(item for item in kind if isinstance(item, str))
            for child in value.values():
                collect_types(child)
        elif isinstance(value, list):
            for child in value:
                collect_types(child)

    for match in pattern.finditer(text):
        try:
            collect_types(json.loads(match.group(1).strip()))
        except json.JSONDecodeError:
            continue

    if "WebPage" in existing_types:
        return text

    payload = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "@id": canonical + "#webpage",
        "url": canonical,
        "name": title,
        "description": description,
        "inLanguage": lang,
        "isPartOf": {"@id": ROOT_URL + "#website"},
        "about": {"@id": ROOT_URL + "#software"},
        "primaryImageOfPage": SOCIAL_URL,
    }
    return add_schema_block(text, payload)


def schema_block(payload: dict) -> str:
    return f"""
  {MARK_SCHEMA_BEGIN}
  <script type="application/ld+json">
{json.dumps(payload, ensure_ascii=False, indent=2)}
  </script>
  {MARK_SCHEMA_END}
"""


def add_schema_block(text: str, payload: dict) -> str:
    text = remove_marked(text, MARK_SCHEMA_BEGIN, MARK_SCHEMA_END)
    return text.replace("</head>", schema_block(payload).rstrip() + "\n</head>", 1)


def breadcrumb(items: list[tuple[str, str]]) -> dict:
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": idx, "name": name, "item": url}
            for idx, (name, url) in enumerate(items, 1)
        ],
    }


def patch_existing_pages() -> None:
    pages = [
        {
            "path": SITE / "index.html", "lang": "en", "canonical": ROOT_URL,
            "title": "ArSonKuPik – VST3 Audio Enhancer Plugin for Windows & macOS",
            "description": "ArSonKuPik is a focused VST3 and standalone audio enhancer plugin for fuller, clearer and more dimensional sound on Windows and macOS.",
            "css": "seo-authority.css", "type": "website",
        },
        {
            "path": SITE / "id/index.html", "lang": "id", "canonical": ROOT_URL + "id/",
            "title": "ArSonKuPik – Plugin Audio Enhancer VST3 untuk Windows & macOS",
            "description": "ArSonKuPik adalah plugin audio enhancer VST3 dan Standalone untuk menghasilkan suara lebih berisi, jernih, dan berdimensi di Windows serta macOS.",
            "css": "../seo-authority.css", "type": "website",
        },
        {
            "path": SITE / "guide/index.html", "lang": "en", "canonical": ROOT_URL + "guide/",
            "title": "ArSonKuPik Guide – VST3, Standalone and Windows Audio Routing",
            "description": "Learn how to use ArSonKuPik as a VST3, Standalone processor, or Windows system-audio enhancer for YouTube and Spotify through VB-CABLE.",
            "css": "../seo-authority.css", "type": "article",
        },
        {
            "path": SITE / "id/guide/index.html", "lang": "id", "canonical": ROOT_URL + "id/guide/",
            "title": "Panduan ArSonKuPik – VST3, Standalone, dan Routing Audio Windows",
            "description": "Panduan menggunakan ArSonKuPik sebagai VST3, aplikasi Standalone, serta audio enhancer YouTube dan Spotify melalui VB-CABLE di Windows.",
            "css": "../../seo-authority.css", "type": "article",
        },
        {
            "path": SITE / "activation/index.html", "lang": "en", "canonical": ROOT_URL + "activation/",
            "title": "Optional ArSonKuPik Activation | Licence and Pricing",
            "description": "Review the optional one-time ArSonKuPik activation, licence rights, pricing, checkout safeguards and continued editing terms after evaluation.",
            "css": "../seo-authority.css", "type": "website",
        },
        {
            "path": SITE / "id/activation/index.html", "lang": "id", "canonical": ROOT_URL + "id/activation/",
            "title": "Aktivasi Opsional ArSonKuPik | Lisensi dan Harga",
            "description": "Pelajari aktivasi satu kali ArSonKuPik, hak lisensi, harga, perlindungan checkout, dan ketentuan melanjutkan editing setelah masa evaluasi.",
            "css": "../../seo-authority.css", "type": "website",
        },
    ]

    for item in pages:
        text = item["path"].read_text(encoding="utf-8")
        text = set_title(text, item["title"])
        text = set_meta_name(text, "description", item["description"])
        text = set_meta_name(text, "robots", "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1")
        text = add_head_block(
            text,
            lang=item["lang"],
            canonical=item["canonical"],
            title=item["title"],
            description=item["description"],
            og_type=item["type"],
        )
        text = ensure_stylesheet(text, item["css"])
        if item["path"].name == "index.html" and item["path"].parent in {SITE, SITE / "id"}:
            text = ensure_home_schema(text, item["lang"], item["canonical"], item["title"])
        if item["path"] in {SITE / "activation/index.html", SITE / "id/activation/index.html"}:
            text = ensure_activation_schema(
                text, item["lang"], item["canonical"], item["title"], item["description"]
            )
        write(item["path"], text)

    # Dedicated Guide structured data.
    for lang, path, canonical, home, guide_name in [
        ("en", SITE / "guide/index.html", ROOT_URL + "guide/", ROOT_URL, "ArSonKuPik Guide"),
        ("id", SITE / "id/guide/index.html", ROOT_URL + "id/guide/", ROOT_URL + "id/", "Panduan ArSonKuPik"),
    ]:
        text = path.read_text(encoding="utf-8")
        payload = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "TechArticle",
                    "@id": canonical + "#article",
                    "url": canonical,
                    "headline": "ArSonKuPik Guide – VST3, Standalone and Windows Audio Routing" if lang == "en" else "Panduan ArSonKuPik – VST3, Standalone, dan Routing Audio Windows",
                    "description": "Beginner guide for VST3, Standalone and Windows system-audio routing." if lang == "en" else "Panduan pemula untuk VST3, Standalone, dan routing system audio Windows.",
                    "inLanguage": lang,
                    "image": SOCIAL_URL,
                    "author": {"@type": "Person", "name": "Mas Ari", "url": "https://github.com/masarray"},
                    "publisher": {"@type": "Organization", "name": "MasArray", "url": "https://github.com/masarray"},
                    "mainEntityOfPage": {"@id": canonical + "#webpage"},
                },
                {
                    "@type": "WebPage",
                    "@id": canonical + "#webpage",
                    "url": canonical,
                    "name": guide_name,
                    "inLanguage": lang,
                    "isPartOf": {"@id": ROOT_URL + "#website"},
                    "primaryImageOfPage": SOCIAL_URL,
                },
                breadcrumb([
                    ("ArSonKuPik", home),
                    (guide_name, canonical),
                ]),
            ],
        }
        text = add_schema_block(text, payload)
        write(path, text)


def p2_hub(lang: str, prefix: str = "") -> str:
    if lang == "id":
        return f"""
  {MARK_HUB_BEGIN}
  <section class="section authority-hub" aria-labelledby="authority-title">
    <div class="container">
      <div class="section-heading centered compact"><span class="eyebrow">Bukti, metode, dan transparansi</span><h2 id="authority-title">Pelajari cara produk diuji dan dinilai.</h2><p class="section-lead">Halaman ini memisahkan klaim produk, metode pengukuran, prosedur A/B, dan konteks pengembang agar pengguna dapat menilai ArSonKuPik secara lebih objektif.</p></div>
      <div class="authority-grid">
        <a href="{prefix}measurements/"><strong>Metode pengukuran</strong><span>Level, peak safety, sample rate, dan batas interpretasi.</span></a>
        <a href="{prefix}audio-comparisons/"><strong>Perbandingan audio</strong><span>Cara melakukan A/B yang tidak bias loudness.</span></a>
        <a href="{prefix}use-cases/windows-system-audio/"><strong>Audio Windows</strong><span>Workflow YouTube dan Spotify melalui VB-CABLE.</span></a>
        <a href="{prefix}about/"><strong>Tentang proyek</strong><span>Prinsip desain, siapa yang membuat, dan sumber resmi.</span></a>
      </div>
    </div>
  </section>
  {MARK_HUB_END}
"""
    return f"""
  {MARK_HUB_BEGIN}
  <section class="section authority-hub" aria-labelledby="authority-title">
    <div class="container">
      <div class="section-heading centered compact"><span class="eyebrow">Evidence, method and transparency</span><h2 id="authority-title">See how the product is tested and judged.</h2><p class="section-lead">These resources separate product claims, measurement method, listening comparison and developer context so ArSonKuPik can be evaluated more objectively.</p></div>
      <div class="authority-grid">
        <a href="{prefix}measurements/"><strong>Measurement method</strong><span>Level, peak safety, sample rate and interpretation limits.</span></a>
        <a href="{prefix}audio-comparisons/"><strong>Audio comparisons</strong><span>How to run an A/B test without loudness bias.</span></a>
        <a href="{prefix}use-cases/windows-system-audio/"><strong>Windows system audio</strong><span>YouTube and Spotify routing through VB-CABLE.</span></a>
        <a href="{prefix}about/"><strong>About the project</strong><span>Design principles, authorship and official sources.</span></a>
      </div>
    </div>
  </section>
  {MARK_HUB_END}
"""


def add_hubs() -> None:
    targets = [
        (SITE / "index.html", "en", "", '<section class="section final-cta">'),
        (SITE / "id/index.html", "id", "", '<section class="section final-cta">'),
        (SITE / "guide/index.html", "en", "../", '<section class="guide-final">'),
        (SITE / "id/guide/index.html", "id", "../", '<section class="guide-final">'),
    ]
    for path, lang, prefix, marker in targets:
        text = path.read_text(encoding="utf-8")
        text = remove_marked(text, MARK_HUB_BEGIN, MARK_HUB_END)
        text = insert_before(text, marker, p2_hub(lang, prefix))
        write(path, text)


@dataclass(frozen=True)
class PageSpec:
    slug: str
    id_slug: str
    kind: str
    en_title: str
    id_title: str
    en_description: str
    id_description: str
    en_h1: str
    id_h1: str
    en_lead: str
    id_lead: str
    en_sections: tuple[tuple[str, str, list[str]], ...]
    id_sections: tuple[tuple[str, str, list[str]], ...]


PAGES = [
    PageSpec(
        "about/", "id/about/", "AboutPage",
        "About ArSonKuPik | Independent DSP Project by Mas Ari",
        "Tentang ArSonKuPik | Proyek DSP Independen Mas Ari",
        "Learn who develops ArSonKuPik, the product principles behind it, how claims are bounded, and where to find official releases and documentation.",
        "Pelajari siapa yang mengembangkan ArSonKuPik, prinsip produknya, batas klaim, serta lokasi rilis dan dokumentasi resmi.",
        "An independent audio project built around musical results and verifiable distribution.",
        "Proyek audio independen yang mengutamakan hasil musikal dan distribusi yang dapat diverifikasi.",
        "ArSonKuPik is developed by Tutorial Mas Ari / MasArray as an independent DSP product. The public site documents what the software does, what it does not promise, and how users can verify official packages.",
        "ArSonKuPik dikembangkan oleh Tutorial Mas Ari / MasArray sebagai produk DSP independen. Website publik menjelaskan fungsi software, batas janji produk, serta cara memverifikasi paket resmi.",
        (
            ("Who makes it", "Technical authorship", ["Mas Ari develops the product direction, listening workflow and public documentation.", "The project is distributed through the official MasArray GitHub repository.", "No reseller, mirror or re-upload is treated as an official source."]),
            ("Product principles", "Musical result before complexity", ["One focused enhancement engine supports every factory starting point.", "Processing stays local during normal operation.", "Evaluation, activation and security disclosures are kept separate from sonic claims."]),
            ("Evidence policy", "No invented measurements", ["Listening claims are presented as intended outcomes, not guaranteed results.", "Numerical claims are published only when the method and test conditions can be described.", "Known limitations and platform warnings remain visible."]),
            ("Official sources", "Where to verify the project", ["GitHub Releases for packages and SHA-256 checksums.", "CHANGELOG for public product changes.", "SECURITY and RELEASE-PROVENANCE for reporting and build traceability."]),
        ),
        (
            ("Siapa pembuatnya", "Kepengarangan teknis", ["Mas Ari mengembangkan arah produk, workflow listening, dan dokumentasi publik.", "Proyek didistribusikan melalui repository GitHub resmi MasArray.", "Reseller, mirror, atau re-upload tidak dianggap sebagai sumber resmi."]),
            ("Prinsip produk", "Hasil musikal sebelum kompleksitas", ["Satu enhancement engine yang fokus mendukung seluruh factory starting point.", "Processing normal tetap berjalan secara lokal.", "Informasi evaluasi, aktivasi, dan keamanan dipisahkan dari klaim sonic."]),
            ("Kebijakan bukti", "Tidak membuat data pengukuran palsu", ["Klaim listening dijelaskan sebagai sasaran desain, bukan hasil yang dijamin.", "Klaim numerik hanya diterbitkan ketika metode dan kondisi uji dapat dijelaskan.", "Batasan dan peringatan platform tetap ditampilkan."]),
            ("Sumber resmi", "Tempat memverifikasi proyek", ["GitHub Releases untuk paket dan checksum SHA-256.", "CHANGELOG untuk perubahan produk publik.", "SECURITY dan RELEASE-PROVENANCE untuk pelaporan dan traceability build."]),
        ),
    ),
    PageSpec(
        "measurements/", "id/measurements/", "TechArticle",
        "ArSonKuPik Measurement Method | Level, Peak and Sample-Rate Checks",
        "Metode Pengukuran ArSonKuPik | Level, Peak, dan Sample Rate",
        "Review the reproducible method used to separate loudness from tone, check peak safety, compare sample rates, and interpret ArSonKuPik measurements responsibly.",
        "Pelajari metode yang dapat diulang untuk memisahkan loudness dari tone, memeriksa peak safety, membandingkan sample rate, dan menafsirkan pengukuran ArSonKuPik.",
        "Measure the signal path before turning a listening preference into a technical claim.",
        "Ukur jalur sinyal sebelum mengubah preferensi listening menjadi klaim teknis.",
        "A useful measurement page must explain the source, route, level, sample rate, capture method and uncertainty. This page defines that protocol without fabricating results that have not been reproduced.",
        "Halaman pengukuran yang berguna harus menjelaskan sumber, routing, level, sample rate, metode capture, dan ketidakpastian. Halaman ini mendefinisikan protokol tersebut tanpa membuat hasil yang belum direproduksi.",
        (
            ("Stage 1", "Establish the reference", ["Capture a loopback or digital reference before inserting the processor.", "Record sample rate, bit depth, interface gain and operating-system enhancements.", "Keep the same file and route for every comparison."]),
            ("Stage 2", "Separate tone from loudness", ["Use normal mode to judge intended impact.", "Use Gain Match for level-equal tonal comparison.", "Report both states instead of treating one as the only valid answer."]),
            ("Stage 3", "Check safety and stability", ["Measure true peak and sample peak at the output.", "Repeat at supported sample rates and practical buffer sizes.", "Look for clipping, denormals, dropouts or unstable gain movement."]),
            ("Interpretation", "State what the test cannot prove", ["A frequency plot does not fully describe perceived depth or transient behaviour.", "One song or one interface cannot establish universal performance.", "A result should include the preset, control values and software version."]),
        ),
        (
            ("Tahap 1", "Tetapkan referensi", ["Capture loopback atau referensi digital sebelum memasukkan processor.", "Catat sample rate, bit depth, gain audio interface, dan enhancement sistem operasi.", "Gunakan file dan routing yang sama untuk setiap perbandingan."]),
            ("Tahap 2", "Pisahkan tone dari loudness", ["Gunakan mode normal untuk menilai impact yang dimaksud.", "Gunakan Gain Match untuk perbandingan tone dengan level setara.", "Laporkan kedua kondisi, bukan menganggap salah satunya selalu paling benar."]),
            ("Tahap 3", "Periksa safety dan stabilitas", ["Ukur true peak dan sample peak pada output.", "Ulangi pada sample rate yang didukung dan buffer praktis.", "Periksa clipping, dropout, denormal, atau pergerakan gain yang tidak stabil."]),
            ("Interpretasi", "Nyatakan batas pembuktian", ["Plot frekuensi tidak sepenuhnya menjelaskan depth atau perilaku transient.", "Satu lagu atau satu audio interface tidak membuktikan performa universal.", "Hasil harus menyertakan preset, nilai kontrol, dan versi software."]),
        ),
    ),
    PageSpec(
        "audio-comparisons/", "id/audio-comparisons/", "TechArticle",
        "How to Compare ArSonKuPik Audio | Fair A/B Listening Method",
        "Cara Membandingkan Audio ArSonKuPik | Metode A/B yang Adil",
        "Use a fair ArSonKuPik A/B listening method with familiar material, normal-impact listening, Gain Match verification, and repeatable notes.",
        "Gunakan metode listening A/B ArSonKuPik yang adil dengan material familiar, mode impact normal, verifikasi Gain Match, dan catatan yang dapat diulang.",
        "A fair comparison answers two different questions: impact and tone.",
        "Perbandingan yang adil menjawab dua pertanyaan berbeda: impact dan tone.",
        "Louder sound is often preferred even when the tonal change is not better. ArSonKuPik therefore separates normal listening from optional level-matched verification.",
        "Suara yang lebih keras sering lebih disukai walaupun perubahan tone belum tentu lebih baik. Karena itu ArSonKuPik memisahkan listening normal dari verifikasi level-matched opsional.",
        (
            ("Question 1", "Do I prefer the intended result?", ["Listen in normal mode with Gain Match off.", "Use familiar music at a comfortable monitor level.", "Judge body, vocal focus, stereo depth, air and fatigue over more than a few seconds."]),
            ("Question 2", "Is the tone better at a similar level?", ["Enable Gain Match and repeat the same passage.", "Avoid changing the monitor volume between states.", "Write down the difference before looking at the control positions."]),
            ("Control variables", "Change one thing at a time", ["Start from Signature Balanced.", "Move one control or one preset per pass.", "Keep the playback section, routing and output device unchanged."]),
            ("Documentation", "Make the result reproducible", ["Record version, preset, sample rate and source file.", "State whether Gain Match was on or off.", "Share short legal audio excerpts only when you have the rights to do so."]),
        ),
        (
            ("Pertanyaan 1", "Apakah hasil yang dimaksud lebih saya sukai?", ["Dengarkan mode normal dengan Gain Match off.", "Gunakan musik familiar pada level monitor yang nyaman.", "Nilai body, fokus vokal, stereo depth, air, dan fatigue lebih dari beberapa detik."]),
            ("Pertanyaan 2", "Apakah tone lebih baik pada level serupa?", ["Aktifkan Gain Match dan ulangi bagian yang sama.", "Jangan mengubah volume monitor di antara kondisi.", "Catat perbedaannya sebelum melihat posisi kontrol."]),
            ("Variabel kontrol", "Ubah satu hal dalam satu waktu", ["Mulai dari Signature Balanced.", "Gerakkan satu kontrol atau satu preset dalam setiap pass.", "Pertahankan bagian playback, routing, dan output device."]),
            ("Dokumentasi", "Buat hasil dapat direproduksi", ["Catat versi, preset, sample rate, dan source file.", "Nyatakan apakah Gain Match on atau off.", "Bagikan potongan audio hanya jika Anda memiliki hak penggunaannya."]),
        ),
    ),
    PageSpec(
        "use-cases/windows-system-audio/", "id/use-cases/windows-system-audio/", "TechArticle",
        "Windows System Audio Enhancer for YouTube and Spotify | ArSonKuPik",
        "Audio Enhancer Windows untuk YouTube dan Spotify | ArSonKuPik",
        "Route YouTube, Spotify, browser and media-player audio through VB-CABLE into ArSonKuPik Standalone, then send the processed signal to your listening device.",
        "Route audio YouTube, Spotify, browser, dan media player melalui VB-CABLE menuju ArSonKuPik Standalone, lalu kirim hasil processing ke perangkat dengar.",
        "Route Windows playback through ArSonKuPik without pretending Standalone captures it automatically.",
        "Route playback Windows melalui ArSonKuPik tanpa menganggap Standalone menangkapnya secara otomatis.",
        "Standalone processes the input you select. To enhance general Windows playback, a virtual cable must carry system audio into that input and a separate real device must receive the processed output.",
        "Standalone memproses input yang dipilih. Untuk meningkatkan playback Windows secara umum, virtual cable harus membawa system audio ke input tersebut dan perangkat nyata yang berbeda menerima output hasil processing.",
        (
            ("Route", "Windows output → CABLE Input", ["Choose CABLE Input as the Windows playback device.", "Applications such as YouTube and Spotify now send audio into the virtual cable.", "If the processor is closed, restore the normal Windows output."]),
            ("Processor input", "CABLE Output → ArSonKuPik", ["Select CABLE Output as the Standalone input.", "Confirm the input meter moves before changing presets.", "Match sample rate where practical."]),
            ("Listening output", "ArSonKuPik → real device", ["Choose speakers, an audio interface, wired headphones or TWS stereo output.", "Do not send the output back to the same virtual-cable endpoint.", "Use wired monitoring when latency matters."]),
            ("Troubleshooting", "Check the route before the DSP", ["No meter movement means the selected input has no signal.", "Meter movement without sound usually indicates the wrong output device.", "Thin Bluetooth sound often means Hands-Free mode instead of Stereo/A2DP."]),
        ),
        (
            ("Routing", "Output Windows → CABLE Input", ["Pilih CABLE Input sebagai playback device Windows.", "YouTube dan Spotify sekarang mengirim audio ke virtual cable.", "Jika processor ditutup, kembalikan output Windows ke perangkat normal."]),
            ("Input processor", "CABLE Output → ArSonKuPik", ["Pilih CABLE Output sebagai input Standalone.", "Pastikan input meter bergerak sebelum mengganti preset.", "Samakan sample rate jika memungkinkan."]),
            ("Output dengar", "ArSonKuPik → perangkat nyata", ["Pilih speaker, audio interface, headphone kabel, atau output TWS Stereo.", "Jangan mengirim output kembali ke endpoint virtual cable yang sama.", "Gunakan monitoring kabel ketika latency penting."]),
            ("Troubleshooting", "Periksa routing sebelum DSP", ["Meter tidak bergerak berarti input yang dipilih tidak membawa sinyal.", "Meter bergerak tetapi tidak ada suara biasanya berarti output device salah.", "Suara Bluetooth tipis sering berarti mode Hands-Free, bukan Stereo/A2DP."]),
        ),
    ),
]


def depth_prefix(slug: str) -> str:
    depth = len([p for p in slug.strip("/").split("/") if p])
    return "../" * depth


def render_cards(sections: tuple[tuple[str, str, list[str]], ...]) -> str:
    cards = []
    for eyebrow, title, bullets in sections:
        li = "".join(f"<li>{escape(x)}</li>" for x in bullets)
        cards.append(f'<article><span>{escape(eyebrow)}</span><h2>{escape(title)}</h2><ul>{li}</ul></article>')
    return "\n        ".join(cards)


def render_page(spec: PageSpec, lang: str) -> tuple[Path, str]:
    is_id = lang == "id"
    slug = spec.id_slug if is_id else spec.slug
    canonical = ROOT_URL + slug
    alternate = ROOT_URL + (spec.slug if is_id else spec.id_slug)
    home = ROOT_URL + ("id/" if is_id else "")
    title = spec.id_title if is_id else spec.en_title
    description = spec.id_description if is_id else spec.en_description
    h1 = spec.id_h1 if is_id else spec.en_h1
    lead = spec.id_lead if is_id else spec.en_lead
    sections = spec.id_sections if is_id else spec.en_sections
    prefix = depth_prefix(slug)
    local_lang = "id" if is_id else "en"
    locale = "id_ID" if is_id else "en_US"
    alt_locale = "en_US" if is_id else "id_ID"
    switch_href = prefix + (spec.slug if is_id else spec.id_slug)
    switch_label = "EN" if is_id else "ID"
    self_label = "ID" if is_id else "EN"
    nav_guide = prefix + ("guide/" if not is_id else "id/guide/")
    nav_measure = prefix + ("measurements/" if not is_id else "id/measurements/")
    nav_about = prefix + ("about/" if not is_id else "id/about/")
    breadcrumb_name = title.split(" | ")[0]
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": spec.kind,
                "@id": canonical + "#content",
                "url": canonical,
                "name": breadcrumb_name,
                "headline": breadcrumb_name,
                "description": description,
                "inLanguage": local_lang,
                "image": SOCIAL_URL,
                "author": {"@type": "Person", "name": "Mas Ari", "url": "https://github.com/masarray"},
                "publisher": {"@type": "Organization", "name": "MasArray", "url": "https://github.com/masarray"},
                "mainEntityOfPage": {"@id": canonical + "#webpage"},
            },
            {
                "@type": "WebPage",
                "@id": canonical + "#webpage",
                "url": canonical,
                "name": breadcrumb_name,
                "inLanguage": local_lang,
                "isPartOf": {"@id": ROOT_URL + "#website"},
                "primaryImageOfPage": SOCIAL_URL,
            },
            breadcrumb([("ArSonKuPik", home), (breadcrumb_name, canonical)]),
        ],
    }
    cards = render_cards(sections)
    labels = {
        "eyebrow": "Sumber teknis ArSonKuPik" if is_id else "ArSonKuPik technical resource",
        "back": "Kembali ke halaman produk" if is_id else "Back to product page",
        "guide": "Panduan penggunaan" if is_id else "Usage guide",
        "method": "Metode pengukuran" if is_id else "Measurement method",
        "about": "Tentang proyek" if is_id else "About the project",
        "official": "Sumber resmi dan verifikasi" if is_id else "Official sources and verification",
        "source_copy": "Unduh hanya dari GitHub Releases resmi, cocokkan SHA-256, dan gunakan dokumentasi publik untuk memeriksa perubahan serta batasan produk." if is_id else "Download only from official GitHub Releases, verify SHA-256, and use public documentation to review product changes and limitations.",
        "release": "Buka rilis resmi" if is_id else "Open official releases",
        "changelog": "Baca changelog" if is_id else "Read the changelog",
        "security": "Keamanan dan provenance" if is_id else "Security and provenance",
    }
    html = f"""<!doctype html>
<html lang="{local_lang}" data-site-base="{prefix.rstrip('/') or '.'}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description, quote=True)}">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="author" content="Tutorial Mas Ari / MasArray">
  <meta name="theme-color" content="#0b0910">
  <meta name="color-scheme" content="dark">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" hreflang="en" href="{ROOT_URL + spec.slug}">
  <link rel="alternate" hreflang="id" href="{ROOT_URL + spec.id_slug}">
  <link rel="alternate" hreflang="x-default" href="{ROOT_URL + spec.slug}">
  <link rel="sitemap" type="application/xml" href="{ROOT_URL}sitemap.xml">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="ArSonKuPik">
  <meta property="og:locale" content="{locale}">
  <meta property="og:locale:alternate" content="{alt_locale}">
  <meta property="og:title" content="{escape(title, quote=True)}">
  <meta property="og:description" content="{escape(description, quote=True)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SOCIAL_URL}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="ArSonKuPik technical guide and audio enhancer interface">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escape(title, quote=True)}">
  <meta name="twitter:description" content="{escape(description, quote=True)}">
  <meta name="twitter:image" content="{SOCIAL_URL}">
  <meta name="twitter:image:alt" content="ArSonKuPik technical guide and audio enhancer interface">
  <link rel="icon" href="{prefix}assets/arsonkupik-vst-favicon.ico" sizes="any">
  <link rel="icon" type="image/png" href="{prefix}assets/arsonkupik-vst-favicon-96.png" sizes="96x96">
  <link rel="stylesheet" href="{prefix}styles.css">
  <link rel="stylesheet" href="{prefix}trial.css">
  <link rel="stylesheet" href="{prefix}hardening-v6.css">
  <link rel="stylesheet" href="{prefix}seo-authority.css">
  <script type="application/ld+json">
{json.dumps(schema, ensure_ascii=False, indent=2)}
  </script>
</head>
<body class="authority-page">
  <a class="skip-link" href="#main">{'Lewati ke konten utama' if is_id else 'Skip to main content'}</a>
  <header class="nav landing-nav"><div class="container nav-inner">
    <a class="brand" href="{prefix}{'id/' if is_id else ''}" aria-label="ArSonKuPik home"><img src="{prefix}assets/arsonkupik-vst-favicon-96.png" width="32" height="32" alt=""><span class="brand-lockup"><b>ARSON<em>KUPIK</em></b><small>{labels['eyebrow']}</small></span></a>
    <nav aria-label="Resource navigation"><a href="{nav_guide}">{labels['guide']}</a><a href="{nav_measure}">{labels['method']}</a><a href="{nav_about}">{labels['about']}</a></nav>
    <div class="nav-actions"><div class="language-switch" aria-label="Language / Bahasa"><a href="{switch_href}" hreflang="{'en' if is_id else 'id'}" lang="{'en' if is_id else 'id'}">{switch_label}</a><a href="./" hreflang="{local_lang}" lang="{local_lang}" aria-current="page">{self_label}</a></div><a class="nav-release" href="{prefix}{'id/' if is_id else ''}#download">{'Unduh' if is_id else 'Download'}</a></div>
  </div></header>
  <main id="main">
    <section class="authority-hero"><div class="container"><span class="eyebrow">{labels['eyebrow']}</span><h1>{escape(h1)}</h1><p class="lead">{escape(lead)}</p><div class="actions"><a class="button primary" href="{prefix}{'id/' if is_id else ''}">{labels['back']}</a><a class="button secondary" href="{nav_guide}">{labels['guide']}</a></div></div></section>
    <section class="section"><div class="container authority-article-grid">{cards}</div></section>
    <section class="section alt"><div class="container authority-source"><div><span class="eyebrow">{labels['official']}</span><h2>{labels['official']}</h2><p>{labels['source_copy']}</p></div><div class="authority-source-links"><a href="https://github.com/masarray/vst-enhancer/releases/latest">{labels['release']}</a><a href="https://github.com/masarray/vst-enhancer/blob/main/CHANGELOG.md">{labels['changelog']}</a><a href="https://github.com/masarray/vst-enhancer/blob/main/RELEASE-PROVENANCE.md">{labels['security']}</a></div></div></section>
  </main>
  <footer><div class="container footer-bottom"><span>© 2026 Tutorial Mas Ari / MasArray.</span><a href="{prefix}{'id/' if is_id else ''}">{labels['back']}</a></div></footer>
</body>
</html>"""
    return SITE / slug / "index.html", html


def create_p2_pages() -> None:
    for spec in PAGES:
        for lang in ("en", "id"):
            path, html = render_page(spec, lang)
            write(path, html)


def write_css() -> None:
    css = r"""
/* P1/P2 search authority pages and internal evidence hub. */
.authority-hub{background:radial-gradient(circle at 15% 15%,rgba(155,104,255,.1),transparent 34%),var(--surface)}
.authority-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px;margin-top:34px}
.authority-grid a{display:flex;min-height:150px;flex-direction:column;padding:22px;border:1px solid rgba(255,255,255,.1);border-radius:16px;background:linear-gradient(145deg,rgba(255,255,255,.04),rgba(255,255,255,.012));color:inherit;text-decoration:none;transition:transform .16s ease,border-color .16s ease}
.authority-grid a:hover,.authority-grid a:focus-visible{transform:translateY(-2px);border-color:rgba(195,157,255,.42)}
.authority-grid strong{font-size:.96rem;color:#f2edf5}.authority-grid span{margin-top:10px;color:#a9a1ae;font-size:.78rem;line-height:1.6}
.authority-page{background:var(--bg)}
.authority-hero{position:relative;overflow:hidden;padding:84px 0 72px;border-bottom:1px solid var(--line);background:radial-gradient(circle at 10% 10%,rgba(145,80,255,.24),transparent 36%),radial-gradient(circle at 88% 48%,rgba(72,194,149,.11),transparent 32%),linear-gradient(180deg,#0d0b12,#111018)}
.authority-hero::before{content:"";position:absolute;inset:0;pointer-events:none;opacity:.18;background-image:linear-gradient(rgba(255,255,255,.02) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.02) 1px,transparent 1px);background-size:44px 44px;mask-image:linear-gradient(to bottom,black,transparent)}
.authority-hero .container{position:relative}.authority-hero h1{max-width:920px;margin:17px 0 0;font-size:clamp(2.5rem,5vw,4.6rem);line-height:1.02;letter-spacing:-.045em}.authority-hero .lead{max-width:830px}
.authority-article-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px}.authority-article-grid article{min-height:280px;padding:27px;border:1px solid rgba(255,255,255,.1);border-radius:18px;background:linear-gradient(150deg,rgba(255,255,255,.044),rgba(255,255,255,.014))}.authority-article-grid article>span{color:#c8a7ff;font-size:.68rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase}.authority-article-grid h2{margin:15px 0 0;font-size:clamp(1.45rem,2.5vw,2.15rem)}.authority-article-grid ul{display:grid;gap:10px;margin:20px 0 0;padding-left:20px;color:#b4acb9;font-size:.84rem;line-height:1.65}
.authority-source{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(280px,.75fr);gap:44px;align-items:center}.authority-source h2{margin:13px 0 0}.authority-source p{max-width:720px;color:var(--muted);line-height:1.7}.authority-source-links{display:grid;gap:10px}.authority-source-links a{padding:14px 16px;border:1px solid rgba(255,255,255,.1);border-radius:12px;color:#dbcaff;background:rgba(255,255,255,.02);text-decoration:none;font-size:.8rem;font-weight:720}
@media(max-width:1000px){.authority-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:760px){.authority-grid,.authority-article-grid,.authority-source{grid-template-columns:1fr}.authority-grid a,.authority-article-grid article{min-height:0}.authority-hero{padding-top:58px}.authority-hero h1{font-size:clamp(2.25rem,10vw,3.25rem)}}
"""
    write(SITE / "seo-authority.css", css)


def sitemap_entries() -> list[str]:
    urls = [
        ROOT_URL,
        ROOT_URL + "id/",
        ROOT_URL + "guide/",
        ROOT_URL + "id/guide/",
        ROOT_URL + "activation/",
        ROOT_URL + "id/activation/",
    ]
    for spec in PAGES:
        urls.extend([ROOT_URL + spec.slug, ROOT_URL + spec.id_slug])
    return urls


def update_sitemaps() -> None:
    urls = sitemap_entries()
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ElementTree.register_namespace("", ns)
    root = ElementTree.Element(f"{{{ns}}}urlset")
    old_dates = {}
    try:
        old = ElementTree.parse(SITE / "sitemap.xml").getroot()
        for node in old.findall(f"{{{ns}}}url"):
            loc = node.findtext(f"{{{ns}}}loc", "").strip()
            old_dates[loc] = node.findtext(f"{{{ns}}}lastmod", "").strip()
    except ElementTree.ParseError:
        pass
    for url in urls:
        item = ElementTree.SubElement(root, f"{{{ns}}}url")
        ElementTree.SubElement(item, f"{{{ns}}}loc").text = url
        ElementTree.SubElement(item, f"{{{ns}}}lastmod").text = old_dates.get(url, TODAY)
    tree = ElementTree.ElementTree(root)
    ElementTree.indent(tree, space="  ")
    backup(SITE / "sitemap.xml")
    tree.write(SITE / "sitemap.xml", encoding="utf-8", xml_declaration=True, short_empty_elements=True)
    print("[WRITE] site/sitemap.xml")
    write(SITE / "sitemap.txt", "\n".join(urls))


def write_validators() -> None:
    specs = []
    specs.extend([
        (ROOT_URL, "site/index.html", "en", ROOT_URL, ROOT_URL + "id/", ["WebSite", "WebPage", "SoftwareApplication"]),
        (ROOT_URL + "id/", "site/id/index.html", "id", ROOT_URL, ROOT_URL + "id/", ["WebPage", "SoftwareApplication"]),
        (ROOT_URL + "guide/", "site/guide/index.html", "en", ROOT_URL + "guide/", ROOT_URL + "id/guide/", ["TechArticle", "BreadcrumbList"]),
        (ROOT_URL + "id/guide/", "site/id/guide/index.html", "id", ROOT_URL + "guide/", ROOT_URL + "id/guide/", ["TechArticle", "BreadcrumbList"]),
        (ROOT_URL + "activation/", "site/activation/index.html", "en", ROOT_URL + "activation/", ROOT_URL + "id/activation/", ["WebPage"]),
        (ROOT_URL + "id/activation/", "site/id/activation/index.html", "id", ROOT_URL + "activation/", ROOT_URL + "id/activation/", ["WebPage"]),
    ])
    for spec in PAGES:
        specs.append((ROOT_URL + spec.slug, f"site/{spec.slug}index.html", "en", ROOT_URL + spec.slug, ROOT_URL + spec.id_slug, [spec.kind, "BreadcrumbList"]))
        specs.append((ROOT_URL + spec.id_slug, f"site/{spec.id_slug}index.html", "id", ROOT_URL + spec.slug, ROOT_URL + spec.id_slug, [spec.kind, "BreadcrumbList"]))
    specs_literal = repr(specs)
    validator = f'''#!/usr/bin/env python3
"""Validate all public ArSonKuPik SEO pages."""
from __future__ import annotations
import json, re, sys
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree
ROOT={ROOT_URL!r}
SOCIAL={SOCIAL_URL!r}
SPECS={specs_literal}
NS="http://www.sitemaps.org/schemas/sitemap/0.9"
class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.lang=""; self.title=""; self._title=False; self.h1=0; self.meta={{}}; self.props={{}}; self.canonical=[]; self.sitemap=[]; self.hreflang={{}}; self.jsonld=[]; self._json=False; self._chunks=[]; self.refresh=False
    def handle_starttag(self,tag,attrs):
        d={{k.lower():v or "" for k,v in attrs}}
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
        expected.append(url); raw=(base/rel).read_bytes(); check(not raw.startswith(b"\\xef\\xbb\\xbf"),f"BOM: {{rel}}")
        p=P(); p.feed(raw.decode("utf-8")); check(p.lang==lang,f"lang: {{url}}"); check(30<=len(p.title.strip())<=78,f"title: {{url}}"); check(70<=len(p.meta.get("description", ""))<=230,f"description: {{url}}"); check(p.h1==1 and not p.refresh,f"H1/refresh: {{url}}")
        robots={{x.strip().lower() for x in p.meta.get("robots","").split(",")}}; check({{"index","follow"}}<=robots and "noindex" not in robots,f"robots: {{url}}")
        check(p.canonical==[url],f"canonical: {{url}}"); check(p.sitemap==[ROOT+"sitemap.xml"],f"sitemap link: {{url}}"); check(p.hreflang=={{"en":en_url,"id":id_url,"x-default":en_url}},f"hreflang: {{url}}")
        check(p.props.get("og:url")==url and p.props.get("og:image")==SOCIAL,f"OG URL/image: {{url}}"); check(p.props.get("og:image:width")=="1200" and p.props.get("og:image:height")=="630",f"OG dimensions: {{url}}")
        for key in ("og:title","og:description","og:image:alt"): check(bool(p.props.get(key)),f"missing {{key}}: {{url}}")
        check(p.meta.get("twitter:card")=="summary_large_image" and p.meta.get("twitter:image")==SOCIAL,f"Twitter: {{url}}")
        for key in ("twitter:title","twitter:description","twitter:image:alt"): check(bool(p.meta.get(key)),f"missing {{key}}: {{url}}")
        all_types=set(); [all_types.update(types(x)) for x in p.jsonld]
        check(set(required)<=all_types,f"schema {{required}} missing at {{url}}; got {{sorted(all_types)}}")
    tree=ElementTree.parse(base/"site/sitemap.xml").getroot(); locs=[n.findtext(f"{{{{{{NS}}}}}}loc","").strip() for n in tree.findall(f"{{{{{{NS}}}}}}url")]
    check(locs==expected and len(locs)==len(set(locs)),"sitemap.xml mismatch"); txt=[x.strip() for x in (base/"site/sitemap.txt").read_text().splitlines() if x.strip()]; check(txt==expected,"sitemap.txt mismatch")
    img=base/"site/assets/arsonkupik-guide-social-1200x630.png"; check(img.exists() and img.stat().st_size>10000,"social PNG missing")
    print(f"[PASS] {{len(expected)}} canonical pages: metadata, social image, schema, hreflang and sitemaps are consistent.")
if __name__=="__main__":
    try: main()
    except Exception as e: print(f"[FAIL] SEO validation: {{e}}"); sys.exit(1)
'''
    write(TOOLS / "validate-seo.py", validator)

    live = f'''#!/usr/bin/env python3
"""Validate deployed ArSonKuPik SEO endpoints after GitHub Pages propagation."""
from __future__ import annotations
import argparse, time, urllib.request, urllib.error, sys
from html.parser import HTMLParser
from xml.etree import ElementTree
ROOT={ROOT_URL!r}
URLS={repr([s[0] for s in specs])}
NS="http://www.sitemaps.org/schemas/sitemap/0.9"
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): return None
class P(HTMLParser):
    def __init__(self): super().__init__(); self.canonical=[]; self.robots=""; self.h1=0
    def handle_starttag(self,t,a):
        d={{k.lower():v or "" for k,v in a}}
        if t=="h1": self.h1+=1
        elif t=="meta" and d.get("name","").lower()=="robots": self.robots=d.get("content","").lower()
        elif t=="link" and "canonical" in d.get("rel","").lower().split(): self.canonical.append(d.get("href",""))
def get(opener,url):
    req=urllib.request.Request(url,headers={{"User-Agent":"ArSonKuPik-SEO-Validator/2.0","Cache-Control":"no-cache"}})
    with opener.open(req,timeout=25) as r: return r.status,dict(r.headers),r.read()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--attempts",type=int,default=12); ap.add_argument("--delay",type=float,default=10); ap.add_argument("--expected-version"); args=ap.parse_args(); opener=urllib.request.build_opener(NoRedirect)
    last=None
    for attempt in range(1,args.attempts+1):
        try:
            for url in URLS:
                status,headers,raw=get(opener,url)
                if status!=200: raise AssertionError(f"{{url}} status {{status}}")
                if "noindex" in headers.get("X-Robots-Tag","").lower(): raise AssertionError(f"X-Robots noindex: {{url}}")
                p=P(); p.feed(raw.decode("utf-8"));
                if p.canonical!=[url] or "index" not in p.robots or "noindex" in p.robots or p.h1!=1: raise AssertionError(f"page signals: {{url}}")
            _,_,raw=get(opener,ROOT+"sitemap.xml"); tree=ElementTree.fromstring(raw.decode("utf-8")); locs=[n.findtext(f"{{{{{{NS}}}}}}loc","").strip() for n in tree.findall(f"{{{{{{NS}}}}}}url")]
            if locs!=URLS: raise AssertionError("live sitemap mismatch")
            print(f"[PASS] Live SEO validation passed for {{len(URLS)}} pages."); return
        except Exception as e:
            last=e
            if attempt<args.attempts: time.sleep(args.delay)
    raise SystemExit(f"[FAIL] Live SEO validation: {{last}}")
if __name__=="__main__": main()
'''
    write(TOOLS / "validate-live-seo.py", live)


def check_image() -> None:
    image = SITE / "assets/arsonkupik-guide-social-1200x630.png"
    if not image.exists():
        fail("PNG asset was not copied. Extract the bundle with folders preserved.")
    try:
        from PIL import Image
        with Image.open(image) as img:
            if img.size != (1200, 630):
                fail(f"Social image must be 1200x630, got {img.size}")
    except ImportError:
        if image.stat().st_size < 10000:
            fail("Social image appears invalid")


def main() -> int:
    require_repo()
    ignore_backup_dir()
    check_image()
    patch_existing_pages()
    write_css()
    create_p2_pages()
    add_hubs()
    update_sitemaps()
    write_validators()
    print("\n[DONE] P1 + P2 files applied.")
    print("Next: python tools/validate-seo.py")
    print("Then review: git diff --check && git status --short")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
