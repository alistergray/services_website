# Construction Data and AI Services Website

This repository contains a simple static website suitable for hosting on GitHub Pages. It showcases consultancy services for the construction industry with example case studies.

## Structure

- `index.html` – homepage listing recent posts
- `services.html` – overview of services offered
- `case-studies.html` – page displaying posts from `data/posts.json`
- `contact.html` – contact details
- `data/posts.json` – edit this file to manage case study/insight entries
- `static/` – CSS and JavaScript assets

## Running locally

Open `index.html` in your browser. If you prefer a local server, you can run:

```bash
python3 -m http.server
```

and navigate to `http://localhost:8000`.

## Deploying to GitHub Pages

1. Commit your changes to the repository.
2. In the repository settings on GitHub, enable **GitHub Pages** and select the `main` branch as the source.
3. The site will be served from `https://<username>.github.io/<repository>/`.

No additional build step is required.
