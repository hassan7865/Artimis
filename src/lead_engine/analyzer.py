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
    
    system_prompt = db_prompt or """You are an expert Technical B2B Lead Analyst. 
Your goal is to identify high-value clients looking for TECHNICAL implementation work.

QUALIFIED TECHNICAL WORK:
- Artificial Intelligence: Building AI systems, LLM integrations, or RAG pipelines.
- Software Development: Web apps (Next.js, React, Node), Mobile apps, or Backend systems.
- Automation & Infra: Python automation, Cloud infrastructure (AWS/Azure), or DevOps.
- Technical Architecture: Designing complex systems or handling scaling issues.

STRICT DISQUALIFICATION (Score 0):
- Pure Marketing: SEO-only, Social Media management, or Lead Gen services.
- Low-skill tasks: Data entry, Virtual Assistants, or manual research.
- Content & Storytelling: Blog writing, sharing experiences, or asking generic advice.
- Freelancer self-promotion: People looking for jobs instead of hiring.

SCORING LOGIC:
- 90-100: "Hot Lead" - Clear technical project, defined stack, and active intent to pay/hire.
- 70-89: "Strong Lead" - Clear technical problem, looking for solutions or experts.
- 1-69: "Weak Lead" - Vague technical interest or "how to" questions that might lead to a project.
- 0: Not technical, irrelevant, or spam.

Always respond with valid JSON only — no markdown, no explanation outside the JSON."""

    user_prompt = f"""Review this Reddit post to determine if it is a qualified TECHNICAL business lead.

[CONTEXT]
SUBREDDIT: r/{post['subreddit']}
TITLE: {post['title']}
BODY: {post['body'][:1500]}
DETECTED KEYWORDS: {', '.join(matched_keywords) if matched_keywords else 'none'}

[TASK]
1. Evaluate if the author is a potential client seeking technical expertise (AI, Web, Software, Automation).
2. Assign a score based on technical depth and hiring intent.
3. Provide a brief analysis of the specific technical opportunity.
4. Draft a direct, value-driven outreach message that references their technical problem. Do NOT use generic greetings like "Hey there". Start directly with value.

[RESPONSE FORMAT]
Return a JSON object with exactly these keys:
{{
  "score": <0-100>,
  "analysis": "<2-3 sentences on the technical opportunity>",
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
