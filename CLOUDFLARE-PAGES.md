# Cloudflare Pages deployment and SEO authority

ArSonKuPik intentionally keeps two public static hosts while assigning only one canonical SEO identity.

## Hosting roles

- Canonical production site: `https://arsonkupik.pages.dev/`
- Compatibility mirror: `https://masarray.github.io/vst-enhancer/`
- Release binaries: GitHub Releases in `masarray/vst-enhancer`

The two website hosts may serve the same product content, but every deployed indexable page, sitemap, hreflang cluster, Open Graph URL and structured-data URL must resolve to the Cloudflare production identity. The GitHub Pages copy remains browsable and useful for compatibility without competing for canonical indexing.

## Cloudflare Pages settings

Use these Git-integrated build settings for the `arsonkupik` project:

```text
Production branch: main
Framework preset: None
Build command: python3 tools/render-deployment-seo.py --site-dir site
Build output directory: site
Root directory: [empty / repository root]
```

Do not change the Cloudflare build command back to `exit 0`. The source tree intentionally retains the historically reviewed GitHub Pages URLs; `render-deployment-seo.py` rewrites the deploy artifact to the Cloudflare canonical identity before Pages uploads it.

## GitHub Pages mirror

`.github/workflows/pages.yml` validates the source tree first, renders the same Cloudflare canonical identity in the workflow checkout, removes the Cloudflare-only `_headers` file, and then publishes the rendered site to GitHub Pages.

This means the GitHub mirror remains available at its original URLs while its HTML and discovery files point search engines to the matching Cloudflare URLs.

## Preview deployments

`site/_headers` uses absolute `https://arsonkupik.pages.dev/...` production-host rules. It must not add a global `X-Robots-Tag: index` rule. Cloudflare Pages preview deployments use their platform `X-Robots-Tag: noindex` protection, and the production-only header rules must not weaken that behavior.

## Validation

Source contract:

```bash
python3 tools/validate-seo.py
```

Rendered artifact contract:

```bash
cp -a site /tmp/arsonkupik-site
python3 tools/render-deployment-seo.py --site-dir /tmp/arsonkupik-site
python3 tools/validate-live-seo.py \
  --static-dir /tmp/arsonkupik-site \
  --expected-version v0.5.23
```

Live dual-host contract:

```bash
python3 tools/validate-live-seo.py --expected-version v0.5.23
```

The live validator checks Cloudflare as the canonical host and GitHub Pages as the mirror, including canonical tags, hreflang, schema, sitemaps, social-image URLs, release metadata and Cloudflare production HTTP `Link` canonical headers.

## Search-console and backlink policy

Treat `https://arsonkupik.pages.dev/` as the primary URL in search-console submissions, public profiles, documentation, videos and third-party product listings. Keep the GitHub Pages URL operational, but do not promote it as the preferred product website.

If a custom brand domain is adopted later, perform that migration deliberately as a separate project rather than introducing a second canonical host in parallel.
