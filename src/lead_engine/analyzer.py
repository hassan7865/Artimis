import json
import logging
from openai import AzureOpenAI
from .config import CONFIG

log = logging.getLogger("leadgen.analyzer")

# Hardcoded INTENT_MAP removed as per user request to rely strictly on dynamic keywords.

_ai_client = None

def get_ai_client() -> AzureOpenAI:
    global _ai_client
    if _ai_client is None:
        _ai_client = AzureOpenAI(
            azure_endpoint=CONFIG["AZURE_OPENAI_ENDPOINT"],
            api_key=CONFIG["AZURE_OPENAI_API_KEY"],
            api_version=CONFIG["AZURE_OPENAI_API_VERSION"],
        )
    return _ai_client

def detect_intents(text: str, keywords: list[str]) -> tuple[list[str], list[str]]:
    lower = text.lower()
    matched = [kw for kw in keywords if kw.lower() in lower]

    # Intents are now strictly derived from dynamic keywords if needed, 
    # but we return an empty list here to avoid hardcoded assumptions.
    return [], matched

def keyword_score(matched_keywords: list[str], upvotes: int, intents: list[str]) -> int:
    if not matched_keywords:
        return 0
        
    score = 25 # Base score for having at least one match
    score += min(len(matched_keywords) * 15, 40)
    score += min(upvotes // 5, 20)
    return min(score, 100)

from .database import get_ai_prompt

async def analyse_with_gpt(post: dict, intents: list[str], matched_keywords: list[str]) -> dict:
    db_prompt = await get_ai_prompt()
    
    system_prompt = db_prompt or """You are a B2B Lead Analyst specializing in identifying ACTIVE HIRING posts — people who are ready to pay someone RIGHT NOW to build something for them.

WHAT WE'RE LOOKING FOR:
A business owner, founder, or company that is actively posting to find a developer, agency, or freelancer to build or maintain a technical project. They should show clear intent, a defined problem, and willingness to pay.

QUALIFIED SIGNALS (these indicate a real job/contract):
- Explicit hiring language: "looking to hire", "need a dev", "anyone available", "taking on clients", "DM me your rates", "open to proposals"
- Budget or compensation mentioned (even rough: "$500", "paid project", "reasonable budget", "equity + cash")
- Defined deliverable: "build a dashboard", "integrate Stripe", "set up CI/CD", "create an AI chatbot"
- Urgency or timeline: "ASAP", "need this done by X", "launching next month"
- Startup or business context: they mention their product, company, or user base

STRICT DISQUALIFICATION (Score 0 — DO NOT flag these):
- People looking for jobs themselves: "I'm a dev looking for work", "available for freelance", "portfolio link"
- Advice-seeking only: "how do I find a developer?", "what's the best stack for X?" — no hiring intent
- Pure sharing: "I built X", "my app does Y" — experience posts with no hiring
- Vague complaints with no action: "I hate my current dev"
- Marketing/content work only: copywriting gigs, social media management, blog posts

SCORING:
- 90-100: "Hot Lead" — explicit hire intent, budget mentioned, clear deliverable, technical work (dev, AI, automation)
- 70-89: "Strong Lead" — clear hire intent, technical project, no explicit budget but context shows willingness to pay
- 40-69: "Warm Lead" — indirect hire signal (e.g. frustrated with a technical problem, asking for referrals to devs/agencies)
- 1-39: "Cold" — weak signal, mostly advice-seeking or sharing
- 0: Not a lead. Disqualify entirely.

KEY RULE: If the post does not show that the person wants to HIRE or PAY someone, the score must be below 40.

Always respond with valid JSON only — no markdown, no explanation outside the JSON."""

    user_prompt = f"""Review this Reddit post and determine whether the author is actively looking to HIRE or PAY someone for technical work.

[CONTEXT]
SUBREDDIT: r/{post['subreddit']}
TITLE: {post['title']}
BODY: {post['body'][:1500]}
DETECTED KEYWORDS: {', '.join(matched_keywords) if matched_keywords else 'none'}

[TASK]
1. Determine if this is an active hiring/job post — someone who wants to pay a developer, agency, or freelancer.
2. Assign a score based on hiring intent and clarity of the technical work required.
3. Summarise the specific opportunity: what they need built and any budget/timeline signals.
4. Draft a short, direct outreach DM that speaks to their exact need. Do NOT use generic greetings. Start with value.

[RESPONSE FORMAT]
Return a JSON object with exactly these keys:
{{
  "score": <0-100>,
  "analysis": "<2-3 sentences on the hiring opportunity and what they need>",
  "outreach": "<3-4 sentence professional, non-salesy Reddit DM>"
}}"""

    try:
        client = get_ai_client()
        response = client.chat.completions.create(
            model=CONFIG["AZURE_OPENAI_DEPLOYMENT"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=600,
            response_format={"type": "json_object"}
        )
        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)
        
        return {
            "score":    int(parsed.get("score", 50)),
            "analysis": parsed.get("analysis", ""),
            "outreach": parsed.get("outreach", ""),
            "_log": {
                "input": f"SYSTEM: {system_prompt}\nUSER: {user_prompt}",
                "output": raw,
                "tokens": response.usage.total_tokens if response.usage else 0
            }
        }
    except Exception as e:
        log.warning("GPT call failed: %s", e)
        return {
            "score": 40, 
            "analysis": f"AI error: {e}", 
            "outreach": "",
            "_log": {"input": user_prompt, "output": str(e), "tokens": 0}
        }
