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


# SEO Context for all pages
SEO_CONTEXT = {
    'index': {
        'title': 'PeakOps Automation | Workflow Automation & Productivity Engineering',
        'meta_description': 'Streamline workflows with AI-powered automation. Save hours every week on recurring tasks. Expert workflow optimization for busy professionals.',
        'og_title': 'PeakOps Automation | Workflow Automation & Productivity',
        'og_description': 'Transform your workflow. Save hours every week with custom automation solutions.',
        'canonical': '/',
    },
    'about': {
        'title': 'About PeakOps Automation | Our Mission & Expertise',
        'meta_description': 'Learn how PeakOps helps businesses automate workflows and increase productivity. Discover our automation expertise and proven methodology.',
        'og_title': 'About PeakOps Automation',
        'og_description': 'Discover how we help professionals work smarter, not harder through automation.',
        'canonical': '/about',
    },
    'services': {
        'title': 'Automation Services | Workflow & Process Automation Solutions',
        'meta_description': 'Custom automation services including RPA, workflow optimization, data automation, and integration. Tailored solutions for your business.',
        'og_title': 'Automation Services | PeakOps',
        'og_description': 'Transform your business with custom automation solutions.',
        'canonical': '/services',
    },
    'pricing': {
        'title': 'Pricing | Automation Services | Flexible Plans',
        'meta_description': 'Affordable automation pricing plans. Monthly retainers, project-based, and enterprise solutions. Find the right plan for your business.',
        'og_title': 'Pricing | PeakOps Automation',
        'og_description': 'Flexible pricing for automation services that fit your budget.',
        'canonical': '/pricing',
    },
    'results': {
        'title': 'Results & Case Studies | Automation Success Stories',
        'meta_description': 'See real results from our automation projects. Client testimonials, metrics, and success stories. Proven ROI from workflow automation.',
        'og_title': 'Results & Case Studies | PeakOps',
        'og_description': 'Proven automation results. See how we help clients save time and money.',
        'canonical': '/results',
    },
    'faq': {
        'title': 'FAQ | Automation Questions & Answers',
        'meta_description': 'Frequently asked questions about workflow automation, RPA, and productivity solutions. Get answers to common automation concerns.',
        'og_title': 'FAQ | PeakOps Automation',
        'og_description': 'Common questions about automation answered by experts.',
        'canonical': '/faq',
    },
    'contact': {
        'title': 'Contact Us | Get Your Automation Started',
        'meta_description': 'Contact PeakOps Automation. Book a consultation to discuss your workflow automation needs and get started today.',
        'og_title': 'Contact PeakOps | Schedule Your Automation Consultation',
        'og_description': 'Ready to automate? Contact us for a free consultation.',
        'canonical': '/contact',
    },
    'workflow_checklist': {
        'title': 'Workflow Audit Checklist | Free Automation Assessment',
        'meta_description': 'Free workflow audit checklist. Identify automation opportunities in your business process. Download our automation assessment tool.',
        'og_title': 'Workflow Audit Checklist | Free Assessment',
        'og_description': 'Identify automation opportunities with our free checklist.',
        'canonical': '/workflow-checklist',
    },
    'top_10_automations': {
        'title': 'Top 10 Automations for Small Teams | Free Guide',
        'meta_description': 'Discover the top 10 automation opportunities for small teams. Free guide to improving productivity and saving time.',
        'og_title': 'Top 10 Automations | Small Team Guide',
        'og_description': 'The best automation opportunities for your team.',
        'canonical': '/top-10-automations',
    },
    'automation_guide': {
        'title': 'Automation Guide | How to Automate Your Workflows',
        'meta_description': 'Complete guide to workflow automation. Learn automation best practices, tools, and strategies to optimize your business processes.',
        'og_title': 'Automation Guide | Learn to Automate',
        'og_description': 'Everything you need to know about workflow automation.',
        'canonical': '/automation-guide',
    },
    'self_assessment': {
        'title': 'Productivity Self-Assessment | Discover Your Potential',
        'meta_description': 'Take our free productivity assessment. Discover your automation potential and get personalized recommendations.',
        'og_title': 'Productivity Assessment | PeakOps',
        'og_description': 'Assess your productivity potential.',
        'canonical': '/self-assessment',
    },
    'resources': {
        'title': 'Resources | Automation Tools & Learning Materials',
        'meta_description': 'Free automation resources, tools, templates, and learning materials. Everything you need to get started with workflow automation.',
        'og_title': 'Resources | PeakOps',
        'og_description': 'Free automation resources and tools.',
        'canonical': '/resources',
    },
}

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
    seo = SEO_CONTEXT["index"]
    return render_template("index.html", seo=seo)

@app.route("/about")
def about():
    seo = SEO_CONTEXT["about"]
    return render_template("about.html", seo=seo)

@app.route("/services")
def services():
    seo = SEO_CONTEXT["services"]
    return render_template("services.html", seo=seo)

@app.route("/pricing")
def pricing():
    seo = SEO_CONTEXT["pricing"]
    return render_template("pricing.html", seo=seo)

@app.route("/results")
def results():
    seo = SEO_CONTEXT["results"]
    return render_template("results.html", seo=seo)

@app.route("/faq")
def faq():
    """Frequently Asked Questions page."""
    return render_template("faq.html")

@app.route("/self-assessment")
def self_assessment():
    seo = SEO_CONTEXT["self_assessment"]
    return render_template("self_assessment.html", seo=seo)

@app.route("/resources")
def resources():
    seo = SEO_CONTEXT["resources"]
    return render_template("resources.html", seo=seo)

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
