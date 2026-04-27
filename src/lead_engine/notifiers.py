import smtplib
import requests
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import CONFIG

log = logging.getLogger("leadgen.notifiers")

def notify_slack(lead: dict):
    webhook = CONFIG["SLACK_WEBHOOK_URL"]
    if not webhook:
        return
    score = lead["score"]
    emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
    payload = {
        "text": f"{emoji} *New Lead — Score {score}/100*",
        "attachments": [{
            "color":  "#1D9E75" if score >= 70 else "#BA7517",
            "fields": [
                {"title": "Title",     "value": lead["title"],     "short": False},
                {"title": "Subreddit", "value": f"r/{lead['subreddit']}", "short": True},
                {"title": "Author",    "value": lead["author"],    "short": True},
                {"title": "Intents",   "value": lead["intents"],   "short": True},
                {"title": "Upvotes",   "value": str(lead["upvotes"]), "short": True},
                {"title": "Analysis",  "value": lead["ai_analysis"], "short": False},
                {"title": "Outreach",  "value": lead["ai_outreach"], "short": False},
                {"title": "Link",      "value": lead["url"],       "short": False},
            ],
            "footer": f"LeadRadar · {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        }]
    }
    try:
        resp = requests.post(webhook, json=payload, timeout=8)
        resp.raise_for_status()
        log.info("  Slack notification sent for post %s", lead["post_id"])
    except Exception as e:
        log.warning("  Slack notify failed: %s", e)

def notify_email(lead: dict):
    cfg = CONFIG
    if not all([cfg["SMTP_HOST"], cfg["SMTP_USERNAME"], cfg["SMTP_FROM"]]):
        return
    score = lead["score"]
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[LeadRadar] Score {score} — {lead['title'][:60]}"
    msg["From"]    = cfg["SMTP_FROM"]
    msg["To"]      = cfg["SMTP_FROM"] # Sending to self as notification

    body = f"""New lead detected!

Score:     {score}/100
Subreddit: r/{lead['subreddit']}
Author:    {lead['author']}
Intents:   {lead['intents']}
Upvotes:   {lead['upvotes']}
URL:       {lead['url']}

TITLE:
{lead['title']}

AI ANALYSIS:
{lead['ai_analysis']}

SUGGESTED OUTREACH:
{lead['ai_outreach']}
"""
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(cfg["SMTP_HOST"], cfg["SMTP_PORT"]) as server:
            server.starttls()
            server.login(cfg["SMTP_USERNAME"], cfg["SMTP_PASSWORD"])
            server.sendmail(cfg["SMTP_FROM"], cfg["SMTP_FROM"], msg.as_string())
        log.info("  Email notification sent for post %s", lead["post_id"])
    except Exception as e:
        log.warning("  Email notify failed: %s", e)
