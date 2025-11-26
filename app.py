from flask import Flask, render_template, request, redirect, url_for, flash
import os
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-key")


def send_email_notification(form_data: dict):
    """Send an email to you with the contact form details."""
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    to_email = os.environ.get("CONTACT_TO")

    # If any of these are missing, just skip email sending
    if not all([smtp_server, smtp_user, smtp_pass, to_email]):
        print("Email not sent: SMTP env vars not fully configured.")
        return

    msg = EmailMessage()
    msg["Subject"] = "New PeakOps Automation Contact Form Submission"
    msg["From"] = smtp_user
    msg["To"] = to_email

    body = f"""
New contact form submission from PeakOps Automation:

Name: {form_data.get('name')}
Email: {form_data.get('email')}
Company: {form_data.get('company')}
Role: {form_data.get('role')}

What they want to improve/automate:
{form_data.get('improvements')}

Current process:
{form_data.get('current_process')}

Budget range:
{form_data.get('budget')}

---
This message was generated automatically by your website.
"""
    msg.set_content(body)

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print("Email notification sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")


def log_to_google_sheets(form_data: dict):
    """
    Append the form data directly to a Google Sheet using
    a service account + gspread.
    """
    # Spreadsheet ID from env var (required)
    sheet_id = os.environ.get("GOOGLE_SHEETS_ID")
    if not sheet_id:
        print("GOOGLE_SHEETS_ID not set; skipping Google Sheets logging.")
        return

    # Path to the service account JSON
    creds_path = os.environ.get(
        "G_SHEETS_CREDS_PATH",
        "credentials/peakops-3bafb19b9225.json"  # default to your current filename
    )

    if not os.path.exists(creds_path):
        print(f"Credentials file not found at {creds_path}; skipping Google Sheets logging.")
        return

    try:
        creds = Credentials.from_service_account_file(
            creds_path,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id).sheet1

        # Build the row in the order matching your sheet headers
        row = [
            datetime.now().isoformat(timespec="seconds"),
            form_data.get("name", ""),
            form_data.get("email", ""),
            form_data.get("company", ""),
            form_data.get("role", ""),
            form_data.get("improvements", ""),
            form_data.get("current_process", ""),
            form_data.get("budget", ""),
        ]

        sheet.append_row(row)
        print("Logged contact form submission to Google Sheets.")
    except Exception as e:
        print(f"Error logging to Google Sheets: {e}")


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

        # Basic validation
        if not form_data["name"] or not form_data["email"] or not form_data["improvements"]:
            flash("Please fill in all required fields.", "error")
            return render_template("contact.html")

        # Log to Google Sheets
        log_to_google_sheets(form_data)

        # Send email notification
        send_email_notification(form_data)

        flash("Thanks, your message has been received. We'll get back to you shortly.", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
