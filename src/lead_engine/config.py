import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    # ── Azure OpenAI ──────────────────────────────────────────────────────────
    "AZURE_OPENAI_ENDPOINT":    os.getenv("AZURE_OPENAI_ENDPOINT",    "https://openai-ghaia-customers-only.openai.azure.com/"),
    "AZURE_OPENAI_API_KEY":     os.getenv("AZURE_OPENAI_API_KEY",     ""),
    "AZURE_OPENAI_DEPLOYMENT":  os.getenv("AZURE_OPENAI_DEPLOYMENT",  "gpt-4o"),
    "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),

    # ── Database ───────────────────────────────────────────────────────────────
    "MONGODB_URI": os.getenv("MONGODB_URI", ""),
    "MONGODB_DB_NAME": os.getenv("MONGODB_DB_NAME", "lead_engine"),

    # ── Scan settings ─────────────────────────────────────────────────────────
    "POSTS_PER_SUBREDDIT": int(os.getenv("POSTS_PER_SUBREDDIT", "50")),
    "MIN_SCORE_TO_NOTIFY": int(os.getenv("MIN_SCORE_TO_NOTIFY", "70")),
    "MIN_PRESCORE_FOR_AI": int(os.getenv("MIN_PRESCORE_FOR_AI", "25")),
    "MIN_POST_AGE_MINUTES": int(os.getenv("MIN_POST_AGE_MINUTES", "60")),
    "MAX_POST_AGE_MINUTES": int(os.getenv("MAX_POST_AGE_MINUTES", "180")),
    "REQUEST_DELAY_SEC":   float(os.getenv("REQUEST_DELAY_SEC", "2.0")),
    "SCAN_INTERVAL_MINUTES": int(os.getenv("SCAN_INTERVAL_MINUTES", "5")),

    # ── Slack (optional) ──────────────────────────────────────────────────────
    "SLACK_WEBHOOK_URL": os.getenv("SLACK_WEBHOOK_URL", ""),

    # ── Email (optional) ──────────────────────────────────────────────────────
    "SMTP_HOST":     os.getenv("SMTP_HOST", ""),
    "SMTP_PORT":     int(os.getenv("SMTP_PORT", "587")),
    "SMTP_USERNAME": os.getenv("SMTP_USERNAME", ""),
    "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", ""),
    "SMTP_FROM":     os.getenv("SMTP_FROM", ""),
}
