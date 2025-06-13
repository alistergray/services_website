# Construction Data and AI Services Website

This repository contains a minimal Python-based website with a lightweight CMS designed for showcasing consultancy services in the construction industry.

## Features

- Responsive design using basic HTML and CSS
- Admin login with ability to create, edit and delete posts (case studies/insights)
- Contact form
- Content stored in a local SQLite database

## Running the site

1. Ensure Python 3 is installed.
2. Run the server:

```bash
python3 server.py
```

The site will be available at `http://localhost:8000`.

- Access the admin area at `http://localhost:8000/admin`.
- Default credentials: **admin / admin**

## Notes

This is a simplified CMS using only Python standard library modules to avoid external dependencies. It is intended as a demonstration and starting point. For a production deployment, consider a full-featured platform such as WordPress or a hosted CMS with proper security and scalability measures.
