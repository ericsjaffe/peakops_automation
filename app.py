from flask import Flask, render_template, request, redirect, url_for, flash, Response
import os
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-key")


def log_to_google_sheets(form_data: dict) -> None:
    """
    POST the form data to a Google Apps Script Web App that writes to a Sheet
    and sends an email.
    """
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


@app.route("/health", methods=["GET"])
def health():
    """Simple health-check endpoint for uptime monitoring / Render probes."""
    return {"status": "ok"}, 200


@app.route("/sitemap.xml", methods=["GET"])
def sitemap_xml() -> Response:
    """
    XML sitemap used by search engines.

    IMPORTANT:
    - Served with Content-Type: application/xml so Google can parse it.
    - This must be the ONLY /sitemap.xml route in this file.
    """
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

    sitemap_body = "\n".join(xml_lines)
    return Response(sitemap_body, mimetype="application/xml")


@app.route("/robots.txt", methods=["GET"])
def robots_txt() -> Response:
    content = """User-agent: *
Allow: /

Sitemap: https://peakops.club/sitemap.xml
"""
    return Response(content, mimetype="text/plain")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/pricing")
def pricing():
    return render_template("pricing.html")


@app.route("/results")
def results():
    return render_template("results.html")


@app.route("/self-assessment")
def self_assessment():
    return render_template("self_assessment.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        form_data = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "company": request.form.get("company", "").strip(),
            "role": request.form.get("role", "").strip(),
            "improvements": request.form.get("improvements", "").strip(),
            "current_process": request.form.get("current_process", "").strip(),
            "budget": request.form.get("budget", "").strip(),
        }

        # Log to Google Sheets (and trigger email via Apps Script)
        log_to_google_sheets(form_data)

        flash("Thanks, your message has been received. We'll get back to you shortly.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")


if __name__ == "__main__":
    # In production (Render), a WSGI server like gunicorn will run the app instead.
    app.run(host="0.0.0.0", port=5000, debug=True)
