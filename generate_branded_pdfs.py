#!/usr/bin/env python3
"""
Generate branded PeakOps PDFs with logo, colors, and professional layout.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
import os

# PeakOps Brand Colors
PEAKOPS_BLUE = HexColor('#2563eb')
PEAKOPS_CYAN = HexColor('#22d3ee')
PEAKOPS_DARK = HexColor('#0f172a')
PEAKOPS_GRAY = HexColor('#64748b')
PEAKOPS_LIGHT_BG = HexColor('#f8fafc')

class BrandedPDFTemplate:
    """Base class for creating branded PeakOps PDFs"""
    
    def __init__(self, filename, title):
        self.filename = filename
        self.title = title
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles for PeakOps branding"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='PeakOpsTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=PEAKOPS_BLUE,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='PeakOpsHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=PEAKOPS_BLUE,
            spaceBefore=20,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Subheading style
        self.styles.add(ParagraphStyle(
            name='PeakOpsSubHeading',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=PEAKOPS_DARK,
            spaceBefore=14,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='PeakOpsBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=PEAKOPS_DARK,
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            leading=16
        ))
        
        # Bullet style
        self.styles.add(ParagraphStyle(
            name='PeakOpsBullet',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=PEAKOPS_DARK,
            leftIndent=20,
            spaceAfter=6,
            leading=14
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='PeakOpsFooter',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=PEAKOPS_GRAY,
            alignment=TA_CENTER
        ))
    
    def add_header(self):
        """Add PeakOps branded header with logo"""
        # Try to add logo if it exists
        logo_path = 'static/img/peakops-logo.png'
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=1.5*inch, height=0.5*inch)
            self.story.append(logo)
            self.story.append(Spacer(1, 0.2*inch))
        else:
            # Fallback text header
            header = Paragraph("PeakOps<br/>Automation", self.styles['PeakOpsTitle'])
            self.story.append(header)
            self.story.append(Spacer(1, 0.1*inch))
        
        # Add tagline
        tagline = Paragraph(
            "<i>Your productivity engineers for modern teams.</i>",
            self.styles['PeakOpsFooter']
        )
        self.story.append(tagline)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_footer_page(self):
        """Add branded footer page with contact info"""
        self.story.append(PageBreak())
        
        # Contact section
        contact_header = Paragraph("Get Started with PeakOps", self.styles['PeakOpsHeading'])
        self.story.append(contact_header)
        self.story.append(Spacer(1, 0.2*inch))
        
        contact_text = Paragraph(
            """Ready to streamline your workflows and save hours every week? 
            PeakOps Automation specializes in building custom automation solutions 
            for busy professionals and small teams.""",
            self.styles['PeakOpsBody']
        )
        self.story.append(contact_text)
        self.story.append(Spacer(1, 0.2*inch))
        
        # Contact details
        contact_details = [
            ["<b>Website:</b>", "peakops.com"],
            ["<b>Email:</b>", "hello@peakops.com"],
            ["<b>Schedule:</b>", "calendly.com/peakops"]
        ]
        
        table = Table(contact_details, colWidths=[1.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), PEAKOPS_DARK),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.4*inch))
        
        # Services overview
        services_text = Paragraph(
            "<b>Our Services:</b>",
            self.styles['PeakOpsSubHeading']
        )
        self.story.append(services_text)
        
        services = [
            "• Free Workflow Triage Call - Quick audit of your biggest time drains",
            "• Workflow Opportunity Report ($195) - Detailed analysis and recommendations",
            "• Automation Build ($495) - Custom automation implementation",
            "• AI Automation Solution ($995) - Intelligent AI-powered workflows"
        ]
        
        for service in services:
            self.story.append(Paragraph(service, self.styles['PeakOpsBullet']))
        
        self.story.append(Spacer(1, 0.3*inch))
        
        # Copyright
        copyright_text = Paragraph(
            "© 2025 PeakOps Automation. All rights reserved.",
            self.styles['PeakOpsFooter']
        )
        self.story.append(copyright_text)
    
    def build(self):
        """Build the PDF document"""
        self.doc.build(self.story)
        print(f"✓ Generated: {self.filename}")


def generate_workflow_audit_checklist():
    """Generate the Workflow Audit Checklist PDF"""
    pdf = BrandedPDFTemplate(
        'static/pdfs/workflow-audit-checklist.pdf',
        'Workflow Audit Checklist'
    )
    
    # Add header
    pdf.add_header()
    
    # Title
    title = Paragraph("Workflow Audit Checklist", pdf.styles['PeakOpsTitle'])
    pdf.story.append(title)
    pdf.story.append(Spacer(1, 0.2*inch))
    
    # Introduction
    intro = Paragraph(
        """This checklist will help you identify automation opportunities in your daily workflows. 
        For each task you perform regularly, ask yourself these questions to determine if it's 
        a good candidate for automation.""",
        pdf.styles['PeakOpsBody']
    )
    pdf.story.append(intro)
    pdf.story.append(Spacer(1, 0.3*inch))
    
    # Checklist sections
    sections = [
        {
            "title": "1. Task Frequency & Volume",
            "items": [
                "☐ Do you perform this task daily or weekly?",
                "☐ Does this task take more than 5 minutes each time?",
                "☐ Do multiple team members perform this same task?",
                "☐ Does the task involve repetitive steps?"
            ]
        },
        {
            "title": "2. Data Movement & Integration",
            "items": [
                "☐ Do you copy data between different apps or systems?",
                "☐ Do you manually update spreadsheets or databases?",
                "☐ Do you send the same information to multiple places?",
                "☐ Do you wait for data from one system to update another?"
            ]
        },
        {
            "title": "3. Communication & Notifications",
            "items": [
                "☐ Do you send similar emails or messages repeatedly?",
                "☐ Do you manually notify people when something happens?",
                "☐ Do you check multiple places for updates or alerts?",
                "☐ Do you forward or copy information between team members?"
            ]
        },
        {
            "title": "4. File & Document Management",
            "items": [
                "☐ Do you manually organize, rename, or move files?",
                "☐ Do you create similar documents from templates?",
                "☐ Do you convert files between different formats?",
                "☐ Do you track versions or changes across multiple files?"
            ]
        },
        {
            "title": "5. Reporting & Analytics",
            "items": [
                "☐ Do you manually compile reports from different sources?",
                "☐ Do you create the same charts or dashboards regularly?",
                "☐ Do you export and format data for presentations?",
                "☐ Do you track KPIs or metrics manually?"
            ]
        },
        {
            "title": "6. Customer & Lead Management",
            "items": [
                "☐ Do you manually enter customer information into your CRM?",
                "☐ Do you qualify or route leads based on specific criteria?",
                "☐ Do you send follow-up sequences manually?",
                "☐ Do you track customer interactions across multiple tools?"
            ]
        },
        {
            "title": "7. Approval & Review Processes",
            "items": [
                "☐ Do you manually route items for approval or review?",
                "☐ Do you check for missing information before processing?",
                "☐ Do you follow up on pending approvals or deadlines?",
                "☐ Do you notify people when approvals are complete?"
            ]
        },
        {
            "title": "8. Scheduling & Calendar Management",
            "items": [
                "☐ Do you manually schedule meetings or appointments?",
                "☐ Do you send calendar invites or reminders?",
                "☐ Do you coordinate availability across team members?",
                "☐ Do you reschedule or update calendar events frequently?"
            ]
        }
    ]
    
    for section in sections:
        # Section heading
        heading = Paragraph(section["title"], pdf.styles['PeakOpsHeading'])
        pdf.story.append(heading)
        pdf.story.append(Spacer(1, 0.1*inch))
        
        # Checklist items
        for item in section["items"]:
            bullet = Paragraph(item, pdf.styles['PeakOpsBullet'])
            pdf.story.append(bullet)
        
        pdf.story.append(Spacer(1, 0.2*inch))
    
    # Scoring section
    pdf.story.append(Spacer(1, 0.2*inch))
    scoring = Paragraph("Scoring Your Results", pdf.styles['PeakOpsHeading'])
    pdf.story.append(scoring)
    pdf.story.append(Spacer(1, 0.1*inch))
    
    scoring_text = Paragraph(
        """Count the number of checkmarks for each task or workflow area. The more boxes 
        you checked, the better candidate it is for automation:<br/><br/>
        <b>5-8 checkmarks:</b> Excellent automation opportunity - high ROI potential<br/>
        <b>3-4 checkmarks:</b> Good automation candidate - worth exploring<br/>
        <b>1-2 checkmarks:</b> Possible automation - may need further evaluation<br/>
        <b>0 checkmarks:</b> Keep manual for now - automation may not be worthwhile""",
        pdf.styles['PeakOpsBody']
    )
    pdf.story.append(scoring_text)
    
    # Add footer contact page
    pdf.add_footer_page()
    
    # Build PDF
    pdf.build()


def generate_top_10_automations():
    """Generate the Top 10 Automations for Small Teams PDF"""
    pdf = BrandedPDFTemplate(
        'static/pdfs/top-10-automations-small-teams.pdf',
        'Top 10 Automations for Small Teams'
    )
    
    # Add header
    pdf.add_header()
    
    # Title
    title = Paragraph("Top 10 Automations<br/>for Small Teams", pdf.styles['PeakOpsTitle'])
    pdf.story.append(title)
    pdf.story.append(Spacer(1, 0.2*inch))
    
    # Introduction
    intro = Paragraph(
        """Small teams often struggle with limited resources and too much manual work. 
        These 10 automations deliver the highest ROI for teams of 2-20 people, helping 
        you save time, reduce errors, and scale without adding headcount.""",
        pdf.styles['PeakOpsBody']
    )
    pdf.story.append(intro)
    pdf.story.append(Spacer(1, 0.3*inch))
    
    # Automations list
    automations = [
        {
            "title": "1. Lead Capture & CRM Entry",
            "description": """Automatically capture leads from forms, emails, or social media 
            and add them to your CRM with proper categorization and tagging. No more manual 
            data entry or lost leads.""",
            "impact": "Time Saved: 5-10 hours/week",
            "tools": "Tools: Zapier, HubSpot, Airtable, Google Forms"
        },
        {
            "title": "2. Email Follow-Up Sequences",
            "description": """Set up automated email sequences that trigger based on customer 
            actions or time delays. Perfect for onboarding, nurture campaigns, or re-engagement.""",
            "impact": "Time Saved: 3-8 hours/week",
            "tools": "Tools: Mailchimp, ActiveCampaign, Gmail, Zapier"
        },
        {
            "title": "3. Invoice & Payment Reminders",
            "description": """Automatically send payment reminders before and after due dates, 
            update accounting systems when payments are received, and flag overdue accounts.""",
            "impact": "Time Saved: 2-5 hours/week",
            "tools": "Tools: QuickBooks, Stripe, PayPal, Xero"
        },
        {
            "title": "4. Meeting Scheduling & Coordination",
            "description": """Let clients and team members self-schedule meetings based on your 
            availability. Automatically send reminders and sync across calendars.""",
            "impact": "Time Saved: 4-6 hours/week",
            "tools": "Tools: Calendly, Acuity Scheduling, Google Calendar"
        },
        {
            "title": "5. Social Media Posting",
            "description": """Schedule and publish content across multiple social platforms from 
            a single dashboard. Repurpose blog posts, auto-share new content, and maintain 
            consistent presence.""",
            "impact": "Time Saved: 3-7 hours/week",
            "tools": "Tools: Buffer, Hootsuite, Later, Zapier"
        },
        {
            "title": "6. Customer Inquiry Routing",
            "description": """Automatically route customer inquiries to the right team member 
            based on keywords, urgency, or customer type. Ensure faster response times.""",
            "impact": "Time Saved: 5-8 hours/week",
            "tools": "Tools: Help Scout, Zendesk, Gmail filters, Slack"
        },
        {
            "title": "7. Weekly Reporting & Dashboards",
            "description": """Auto-generate weekly reports pulling data from multiple sources. 
            Track KPIs, sales metrics, project status, and team performance without manual 
            compilation.""",
            "impact": "Time Saved: 2-4 hours/week",
            "tools": "Tools: Google Data Studio, Tableau, Excel, Airtable"
        },
        {
            "title": "8. File Organization & Backup",
            "description": """Automatically organize, rename, and backup files based on rules. 
            Move completed projects to archives, sync across cloud storage, and prevent data loss.""",
            "impact": "Time Saved: 2-4 hours/week",
            "tools": "Tools: Dropbox, Google Drive, Backblaze, Hazel"
        },
        {
            "title": "9. Task & Project Updates",
            "description": """Sync tasks across project management tools, automatically update 
            stakeholders on progress, and trigger next steps when tasks are completed.""",
            "impact": "Time Saved: 3-6 hours/week",
            "tools": "Tools: Asana, Trello, Monday.com, Slack, Zapier"
        },
        {
            "title": "10. Expense Tracking & Reporting",
            "description": """Automatically capture receipts, categorize expenses, and generate 
            expense reports. Sync with accounting software and flag policy violations.""",
            "impact": "Time Saved: 2-5 hours/week",
            "tools": "Tools: Expensify, Receipt Bank, QuickBooks, Xero"
        }
    ]
    
    for automation in automations:
        # Automation title
        heading = Paragraph(automation["title"], pdf.styles['PeakOpsHeading'])
        pdf.story.append(heading)
        pdf.story.append(Spacer(1, 0.08*inch))
        
        # Description
        desc = Paragraph(automation["description"], pdf.styles['PeakOpsBody'])
        pdf.story.append(desc)
        pdf.story.append(Spacer(1, 0.08*inch))
        
        # Impact and tools
        impact = Paragraph(f"<b>{automation['impact']}</b>", pdf.styles['PeakOpsBullet'])
        pdf.story.append(impact)
        
        tools = Paragraph(f"<i>{automation['tools']}</i>", pdf.styles['PeakOpsBullet'])
        pdf.story.append(tools)
        
        pdf.story.append(Spacer(1, 0.2*inch))
    
    # Getting Started section
    getting_started = Paragraph("Getting Started", pdf.styles['PeakOpsHeading'])
    pdf.story.append(getting_started)
    pdf.story.append(Spacer(1, 0.1*inch))
    
    getting_started_text = Paragraph(
        """Don't try to automate everything at once. Start with 1-2 automations that will 
        have the biggest impact for your team. Focus on tasks that are:<br/><br/>
        • Highly repetitive and time-consuming<br/>
        • Prone to human error<br/>
        • Currently blocking other work<br/>
        • Easy to define with clear rules<br/><br/>
        PeakOps can help you identify the best starting point and build custom automations 
        tailored to your specific workflows. Book a free triage call to get started.""",
        pdf.styles['PeakOpsBody']
    )
    pdf.story.append(getting_started_text)
    
    # Add footer contact page
    pdf.add_footer_page()
    
    # Build PDF
    pdf.build()


if __name__ == '__main__':
    print("Generating branded PeakOps PDFs...")
    print()
    
    # Generate both PDFs
    generate_workflow_audit_checklist()
    generate_top_10_automations()
    
    print()
    print("✅ All PDFs generated successfully!")
    print("   PDFs are located in: static/pdfs/")
