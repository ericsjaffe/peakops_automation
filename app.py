from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    Response,
    send_from_directory,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import requests
import re

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-key")

# Rate limiting to prevent spam
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def is_valid_email(email):
    """Validate email address format."""
    return bool(EMAIL_REGEX.match(email.strip()))

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
    """Add lightweight security and privacy headers to every response."""
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("X-XSS-Protection", "1; mode=block")
    response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors with custom page."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors with custom page."""
    app.logger.error('Server error: %s', str(e))
    return render_template('500.html'), 500

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
        "https://peakops.club/resources",
        "https://peakops.club/faq",
        "https://peakops.club/workflow-checklist",
        "https://peakops.club/top-10-automations",
        "https://peakops.club/automation-guide",
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

@app.route("/faq")
def faq():
    """Frequently Asked Questions page."""
    return render_template("faq.html")

@app.route("/self-assessment")
def self_assessment():
    return render_template("self_assessment.html")

@app.route("/resources")
def resources():
    return render_template("resources.html")

# ========= Workflow Audit Checklist =========

@app.route("/workflow-checklist", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def workflow_checklist():
    if request.method == "POST":
        email = request.form.get("email", "").strip()

        # Validate email
        if not email or not is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("workflow_checklist"))

        # Log email to Google Sheets
        log_to_google_sheets({
            "email": email,
            "source": "Workflow Checklist"
        })

        # Flash success message
        flash("Thanks! Your checklist is downloading now.", "success")

        # Redirect back to the same page with ?download=1
        return redirect(url_for("workflow_checklist", download="1"))

    return render_template("workflow_checklist.html")

@app.route("/workflow-checklist/download")
def workflow_checklist_download():
    pdf_dir = os.path.join(app.root_path, "static", "pdfs")
    return send_from_directory(
        pdf_dir,
        "workflow-audit-checklist.pdf",
        as_attachment=True,
    )

# ========= Top 10 Automations for Small Teams =========

@app.route("/top-10-automations", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def top_10_automations():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()

        # Validate email
        if not email or not is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("top_10_automations"))

        log_to_google_sheets({"email": email, "source": "Top 10 Automations Guide"})
        return redirect(url_for("top_10_automations_download"))

    return render_template("top_10_automations.html")

@app.route("/top-10-automations/download")
def top_10_automations_download():
    pdf_dir = os.path.join(app.root_path, "static", "pdfs")
    return send_from_directory(
        pdf_dir,
        "top-10-automations-small-teams.pdf",
        as_attachment=True,
    )

# ========= Automation Guide / Playbook (Early Access) =========

@app.route("/automation-guide", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def automation_guide():
    if request.method == "POST":
        email = request.form.get("email", "").strip()

        # Validate email
        if not email or not is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("automation_guide"))

        # Log email to Google Sheets
        log_to_google_sheets({
            "email": email,
            "source": "Automation Guide"
        })

        # Flash success message
        flash("Thanks for downloading the Automation Playbook!", "success")
        
        # Redirect back to same page with ?download=1
        return redirect(url_for("automation_guide", download="1"))

    return render_template("automation_guide.html")

@app.route("/contact", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def contact():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        
        # Validate email
        if not email or not is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("contact"))

        form_data = {
            "name": request.form.get("name", "").strip(),
            "email": email,
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
