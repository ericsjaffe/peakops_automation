
# PeakOps Automation Website

This is a simple Flask-based marketing site for **PeakOps Automation**, suitable for deployment on Render.

## Features

- Home page with hero, how-it-works, services overview, pricing preview, and CTA
- Dedicated About, Services, Pricing, and Contact pages
- Contact form that accepts submissions and shows a confirmation message
- Responsive layout with a modern, tech-startup feel

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000 in your browser.

## Deploying to Render

1. Push this project to a GitHub repository.
2. In Render:
   - Create a new **Web Service**.
   - Connect it to your GitHub repo.
   - Choose a Python environment.
   - Use `pip install -r requirements.txt` as the build command.
   - Use `gunicorn app:app` as the start command (or leave as default if Render detects the Procfile).
3. Deploy. Render will build and run the site using the `Procfile`.

You can customize copy, styling, and structure as needed.
