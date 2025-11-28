from flask import Flask, render_template, request, redirect, url_for, flash, Response
import os
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-key")


def log_to_google_sheets(form_data: dict) -> None:
    """POST the form data to a Google Apps Script Web App that writes to a Sheet and sends an email."""
    url = os.environ.get("G_SHEETS_WEBHOOK_URL")
    if not url:
        app.logger.warning("G_SHEETS_WEBHOOK_URL not set; skipping Google Sheets logging.")
        return

    try:
        resp = requests.post(url, json=form_data, timeout=10)
        resp.raise_for_status()
        app.logger.info("Logged to Google Sheets successfully: %s", resp.text[:500])
    except requests.exceptions.RequestException as exc:
        # Don't break the user experience if logging fails; just log the error.
        app.logger.error("Error logging to Google Sheets: %s", exc, exc_info=True)


@app.after_request
def add_security_headers(response):
    """Add a few lightweight security and privacy headers to every response."""
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("X-XSS-Protection", "1; mode=block")
    return response


@app.route("/health")
def health():
    """Simple health-check endpoint for uptime monitoring / Render probes."""
    return {"status": "ok"}, 200


@app.route("/sitemap.xml")
def sitemap_xml() -> Response:
    """XML sitemap used by search engines."""
    pages = [
        "https://peakops.club/",
        "https://peakops.club/services",
        "https://peakops.club/pricing",
        "https://peakops.club/about",
        "https://peakops.club/contact",
        "https://peakops.club/results",
        "https://peakops.club/self-assessment",
    ]

    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for url in pages:
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{url}</loc>")
        xml_lines.append("    <changefreq>weekly</changefreq>")
        xml_lines.append("    <priority>0.8</priority>")
        xml_lines.append("  </url>")

    xml_lines.append("</urlset>")

    sitemap_xml = "\n".join(xml_lines)
    return Response(sitemap_xml, mimetype="application/xml")


@app.route("/robots.txt")
def robots_txt() -> Response:
    content = """User-agent: *
Allow: /

Sitemap: https://peakops.club/sitemap.xml
"""
    return Response(content, mimetype="text/plain")


@app.route("/")
def index():
    return render_template_
