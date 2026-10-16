# Cartography

The Homotopical Cartography project website and its Exploration Charts.
This repository can be maintained independently of Thomas Nikolaus's personal homepage.

## Publish the website

In this repository, choose **Settings → Pages → Build and deployment → Source → GitHub Actions**.
The included `pages.yml` workflow builds and checks the website on every push to `main`, then publishes it.
Pull requests run the build checks without publishing.

The initial project address is `https://thomasnikolaus.github.io/Cartography/`.
The capital **C** in `/Cartography` matters. Do not copy the personal homepage's `CNAME` file here.

## Edit the site

- `index.html`: project introduction, Atlas explanation, and page layout.
- `charts.json`: real Chart records, authors, versions, status, and human review notes.
- `charts/`: PDFs and generated landing pages for real Charts.
- `placeholders/`: the two clearly marked dummy PDFs shown while the catalogue is empty.
- `assets/homotopical-cartography/`: the two map illustrations.
- `Style.css`, `Cartography.css`, and `favicon-mm.png`: the shared academic visual style and MM symbol.
- `site.json`: the public origin, deployment path, and link to the personal homepage.

See [the catalogue guide](tools/cartography/README.md) for adding a real Chart, versioning, and persistent identifiers.
Run `python3 tools/cartography/build.py` before committing catalogue changes; include the generated Chart/version pages with their PDFs and metadata.

## Preview locally

Python 3.10 or newer is sufficient; no additional packages are required.

```sh
python3 tools/cartography/stage.py --output _preview/Cartography
python3 -m http.server 8000 --bind 127.0.0.1 --directory _preview
```

Then open `http://127.0.0.1:8000/Cartography/`.
The staging step checks links and copies only the public website files. Tooling, raw catalogue/configuration files, Git metadata, and this README are excluded from the deployed website.

## Collaborators

Invite contributors through **Settings → Collaborators → Add people** in this repository.
They can maintain this project without receiving access to the separate `homepage` repository.

## A future project domain

For a later address such as `cartography.thomasnikolaus.de`, update `site.json` to use that origin and an empty `base_path`, and configure the domain in GitHub Pages and DNS.
Keep old Chart, version, and PDF addresses reachable when moving a published collection.
The existing homepage should only redirect to this project after the new website is live and checked.
