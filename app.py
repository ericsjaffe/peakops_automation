from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, Response

import os
import requests

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-key")


def log_to_google_sheets(form_data: dict):
    """POST the form data to a Google Apps Script Web App that writes to a Sheet and sends an email."""
    url = os.environ.get("G_SHEETS_WEBHOOK_URL")
    if not url:
        print("G_SHEETS_WEBHOOK_URL not set; skipping Google Sheets logging.")
        return

    try:
        resp = requests.post(url, json=form_data, timeout=10)
        print(f"Sheets response: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Error logging to Google Sheets: {e}")


@app.route("/sitemap.xml")
def sitemap():
    pages = [
        "https://peakops.club/",
        "https://peakops.club/services",
        "https://peakops.club/pricing",
        "https://peakops.club/about",
        "https://peakops.club/contact",
    ]

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for url in pages:
        xml.append("<url>")
        xml.append(f"<loc>{url}</loc>")
        xml.append("<changefreq>weekly</changefreq>")
        xml.append("<priority>0.8</priority>")
        xml.append("</url>")

    xml.append("</urlset>")

    sitemap_xml = "\n".join(xml)
    return Response(sitemap_xml, mimetype="application/xml")

@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt", mimetype="text/plain")


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

@app.route("/robots.txt")
def robots_txt():
    content = """User-agent: *
Allow: /

Sitemap: https://peakops.club/sitemap.xml
"""
    return Response(content, mimetype="text/plain")

@app.route("/sitemap.xml")
def sitemap_xml():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="https://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://peakops.club/</loc>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://peakops.club/services</loc>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://peakops.club/pricing</loc>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://peakops.club/about</loc>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://peakops.club/contact</loc>
    <priority>0.7</priority>
  </url>
</urlset>
"""
    return Response(xml, mimetype="application/xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
