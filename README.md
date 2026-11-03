# Cartography

The Homotopical Cartography project website and its Exploration Charts.
The site uses plain HTML and CSS and needs no local build.

## Add or update a chart

1. Put the PDF directly in `charts/`, using a descriptive filename such as
   `group-completion-commutes-with-infinite-products.pdf`.
2. In `index.html`, under **The Atlas**, copy an existing `<article>` and
   replace the title, author names, and PDF links (title and thumbnail).
   Update the thumbnail's `aria-label` to match the title.
   The optional **About this chart** section can contain a brief description,
   publication status, and a note on what the authors have checked.
3. To change the illustration, choose a sheet from the
   [map index](assets/maps/monte/index.html). Update the thumbnail's image,
   sheet class, and dimensions using the existing article as an example.
4. Open `index.html` in a browser and click the new links. Commit the HTML and
   PDF together, then push or merge the changes into `main`.

Use relative links such as `charts/your-chart.pdf` so the links also work
when you open the file locally. Use a new descriptive filename if you need
to keep a previously shared PDF available alongside a revision.

## Publish the website

In **Settings → Pages → Build and deployment**, set **Source** to
**GitHub Actions**. The **Publish Cartography** workflow copies the public
files and deploys them on pushes to `main`. Pull requests do not publish.
Check **Actions** for the deployment result.

The public address is https://thomasnikolaus.de/Cartography/ (capital C).
The personal homepage is published separately from
`ThomasNikolaus/thomasnikolaus.github.io` with `thomasnikolaus.de` as its
custom domain. This project inherits that domain; leave this repository's
own Custom domain setting empty.
