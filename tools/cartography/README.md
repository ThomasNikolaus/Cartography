# Exploration Charts catalogue

This is the standalone `ThomasNikolaus/Cartography` site. Its files are served
initially at `https://thomasnikolaus.github.io/Cartography/`.

`site.json` at the repository root controls generated URLs:

```json
{
  "origin": "https://thomasnikolaus.github.io",
  "base_path": "/Cartography",
  "homepage_url": "https://thomasnikolaus.de"
}
```

The origin must be HTTPS with no path, query or fragment. `base_path` is either
empty or a clean slash-prefixed path without a trailing slash; its spelling and
capitalization must match the deployed repository path. `homepage_url` is the
absolute HTTPS link back to the personal homepage. A future deployment at
`https://cartography.thomasnikolaus.de/` would use that origin and an empty
`base_path`; configure the custom domain separately in GitHub Pages.

Edit root-level `charts.json`, then run from the site root:

```sh
python3 tools/cartography/build.py
```

Run the build locally for each real Chart addition, then commit the Chart data,
PDFs, updated `index.html`, and generated current/version pages under `charts/`
together. Keep previously generated version pages in the repository: the
fingerprint guard checks those files and cannot detect earlier changes if they
are omitted or removed. The deployment workflow rebuilds before publishing the
static pages, so future Chart additions update the site through the usual
repository workflow. No framework or package installation is needed.
The generator replaces the catalogue marker block in root-level `index.html`,
updates its single canonical link, and creates individual Chart landing pages.
It does not alter other main-page links or add global navigation links.

`charts.json` stays empty until an actual Chart is ready. While it is empty,
the generator displays two clearly labelled dummy PDF entries: “Group completion
commutes with infinite products” and “There is no infinite Künneth”. Their files
live under `placeholders/`. These are layout placeholders,
not actual Chart records, and have no assigned identifiers, authors or review
claims. The first actual Chart automatically replaces both placeholder entries
in the catalogue; the build does not delete the placeholder PDF files.

To add an actual Chart, use this shape (replace all example content and add the
actual PDF before building):

```json
{
  "charts": [
    {
      "id": "HC-0001",
      "versions": [
        {
          "version": "v1",
          "title": "Title of the completed Chart",
          "authors": ["Author One", "Author Two"],
          "date": "2026-10-16",
          "abstract": "A short description of its mathematical content.",
          "status": "Exploration Chart (not peer-reviewed)",
          "human_review": "Replace with a precise account of which arguments the authors have checked and understood, and which claims remain provisional or open.",
          "pdf": "charts/hc-0001/v1/chart.pdf"
        }
      ]
    }
  ]
}
```

Optional fields: `concept_doi` on the Chart, and `doi` and `arxiv` on each version.
Use raw registered identifiers, not URLs; omit fields until they exist. No
identifiers are registered by this script. The highest `vN` is the current
version. Each version carries its own title, authors, date and abstract, so
later authorship changes do not rewrite earlier citations.

`status` and `human_review` are required, nonempty text fields for every version.
Replace the instructional review text in the example before publishing. State
the Chart's actual publication/review status, and describe the scope of human
verification and understanding without implying that all claims are verified.
The catalogue and landing pages label the status explicitly; current and exact
version landing pages also display the human review note.

## Stable references

- Assign `HC-0001`, `HC-0002`, etc. once; never reuse an ID. This is a local
  project identifier, not a registered persistent identifier.
- With the initial Pages configuration, the Chart landing page is
  `/Cartography/charts/hc-0001/`.
  Exact versions have `/v1/`, `/v2/`, etc. Append versions rather than replacing
  old files. The generator fingerprints the core version metadata and PDF;
  changing an already generated version stops the build. Status and human review
  annotations may be updated as review progresses, and DOI/arXiv links may be
  added later; these annotations are not part of the immutable fingerprint.
  Changes to the mathematics/PDF, title, authors, date or abstract require a new
  version. Template and style changes remain possible.
- When changing a domain or deployment path, retain old published Chart,
  version and PDF URLs or provide redirects from each old address. Updating
  only the start-page redirect does not preserve earlier citations.
- To archive a released Chart independently of this homepage, deposit it in
  Zenodo. For the same artefact, supply an existing DOI rather than creating a
  duplicate. Otherwise a DOI can be reserved before publishing and included in
  the PDF. Registration occurs on publication.
- Zenodo's **version DOI** identifies the exact released content; use it in
  precise citations. Its **Concept DOI** represents all versions and currently
  resolves to the latest version. Store these separately.

Official references: [Zenodo DOI reservation](https://help.zenodo.org/docs/deposit/describe-records/reserve-doi/)
and [Zenodo versioning](https://zenodo.org/help/versioning).

PDF paths must be relative to the repository root and point to existing local
files: use `charts/hc-0001/v1/chart.pdf`, not `/Cartography/charts/…` and not the
former homepage's `homotopical-cartography/charts/…` path. The generator adds the
configured URL prefix; source paths never include the deployment base path.
External URLs, traversal and symlinks outside the site are rejected. All text
and link fields are escaped before generating HTML. Missing PDFs, invalid dates,
duplicate IDs or versions stop the build before any generated content changes.
The build intentionally retains old files and does not delete released versions.
`index.html` must contain exactly one canonical link and one ordered
`CHART-CATALOGUE:START` / `CHART-CATALOGUE:END` marker pair.

The landing-page styles and favicon are served from the configured site root.
Keep `Style.css`, `Cartography.css`, `favicon-mm.png`, both placeholder PDFs, and
the images under `assets/homotopical-cartography/` in the deployed output.
Do not copy the personal homepage's `CNAME` into this repository.

Pages remain `noindex, nofollow` while this section is unlisted; remove that
metadata from the main page and generator when public indexing is wanted.
