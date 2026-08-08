# Cloudflare Pages deployment and SEO authority

ArSonKuPik intentionally keeps two public static hosts while assigning only one canonical SEO identity.

## Hosting roles

- Canonical production site: `https://arsonkupik.pages.dev/`
- Compatibility mirror: `https://masarray.github.io/vst-enhancer/`
- Release binaries: GitHub Releases in `masarray/vst-enhancer`

The two website hosts may serve the same product content, but every deployed indexable page, sitemap, hreflang cluster, Open Graph URL and structured-data URL must resolve to the Cloudflare production identity. The GitHub Pages copy remains browsable and useful for compatibility without competing for canonical indexing.

## Cloudflare Pages settings

Keep the `arsonkupik` project as a static Git-integrated Pages deployment:

```text
Production branch: main
Framework preset: None
Build command: exit 0
Build output directory: site
Root directory: [empty / repository root]
```

No Cloudflare Worker, Pages Function or special build command is required. The repository source itself is promoted to the Cloudflare canonical identity, so Cloudflare can continue serving the `site` directory as a lightweight static site.

## Canonical source promotion

PR #35 introduces a one-time, guarded source promotion in `.github/workflows/pages.yml`.

On the first `main` push containing the migration, the workflow:

1. validates the previously reviewed source and release boundary;
2. renders all static SEO URLs from the historical GitHub Pages root to `https://arsonkupik.pages.dev/`;
3. updates the on-site SEO validator to treat Cloudflare as `ROOT`;
4. validates the promoted source; and
5. commits the promoted `site/` tree and validator back to `main` using the workflow token.

The promotion is idempotent. Once the source is canonicalized, later runs detect no migration diff and do not create another commit. The bot-generated commit is also intentionally separate from the release metadata and binary publication flow.

## GitHub Pages mirror

`.github/workflows/pages.yml` continues publishing a complete GitHub Pages copy. The workflow renders/validates Cloudflare canonical URLs before uploading, so the mirror remains available at its historical URLs while its HTML and discovery files tell search engines that Cloudflare is authoritative.

The Cloudflare-only `_headers` file is removed from the GitHub Pages artifact before upload.

## Preview deployments

`site/_headers` uses absolute `https://arsonkupik.pages.dev/...` production-host rules. It must not add a global `X-Robots-Tag: index` rule. Cloudflare Pages preview deployments keep their platform `X-Robots-Tag: noindex` protection, and production-only header rules must not weaken that behavior.

## Validation

Canonical source contract after migration:

```bash
python3 tools/validate-seo.py
```

Rendered artifact contract (also valid during the migration PR before source promotion):

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

## Search Console and backlink policy

Treat `https://arsonkupik.pages.dev/` as the primary URL in Search Console submissions, public profiles, documentation, videos and third-party product listings. Keep the GitHub Pages URL operational, but do not promote it as the preferred product website.

If a custom brand domain is adopted later, perform that migration deliberately as a separate project rather than introducing a second canonical host in parallel.
