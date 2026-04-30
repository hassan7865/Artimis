from __future__ import annotations
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from lead_engine.api.routers.leads import router as leads_router
from lead_engine.api.routers.config import router as config_router
from lead_engine.api.routers.scheduler import router as scheduler_router

from contextlib import asynccontextmanager
from lead_engine.database import get_db


def configure_logging() -> None:
    logger = logging.getLogger("leadgen")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Check Database Connection
    print("------------------------------------------------------------")
    print("DATABASE CHECK: Attempting to connect to MongoDB Atlas...")
    try:
        db = get_db()
        # Ping the server to verify connection
        await db.command("ping")
        print("DATABASE CHECK: SUCCESS! Connected to Lead Engine DB.")
        
        # Automatic Seeding for Lead Generation Use Case
        # Seeds each key independently so partial configs are handled correctly
        print("DATABASE SEED: Checking for missing config keys...")

        default_keywords = [
            "hiring", "looking to hire", "need a developer", "need a dev",
            "freelancer needed", "contractor needed", "developer needed", "engineer needed",
            "agency needed", "budget for", "build an app", "outsource", "quote for",
            "proposal", "shopify expert", "custom solution", "automation help",
            "app development", "mobile app developer", "mvp development", "saas developer",
            "fractional cto", "anyone available", "dm your rates", "paid project",
            "open to proposals", "need someone to", "looking for someone",
            "need help building", "will pay", "willing to pay", "[hiring]", "for hire"
        ]

        default_subreddits = [
            # Dedicated hiring boards — highest signal
            "forhire", "hiring", "jobbit",
            # Freelance/contract work
            "slavelabour", "freelance", "workonline",
            # Startup / founder communities
            "smallbusiness", "entrepreneur", "startups", "SaaS",
            "microsaas", "indiehackers", "EntrepreneurRideAlong", "sideproject",
            # Tech communities where organic hiring happens
            "webdev", "reactjs", "node", "Python", "devops",
            "MachineLearning", "LocalLLaMA", "ChatGPT",
            # Design & ecommerce
            "web_design", "ecommerce", "shopify"
        ]

        default_prompt = """You are a B2B Lead Analyst specializing in identifying ACTIVE HIRING posts — people who are ready to pay someone RIGHT NOW to build something for them.

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

        seed_configs = {
            "keywords": ",".join(default_keywords),
            "subreddits": ",".join(default_subreddits),
            "ai_prompt": default_prompt,
        }
        seeded = []
        for key, value in seed_configs.items():
            existing = await db.config.find_one({"key": key})
            if not existing:
                await db.config.insert_one({"key": key, "value": value})
                seeded.append(key)
        if seeded:
            print(f"DATABASE SEED: SUCCESS! Seeded missing keys: {', '.join(seeded)}")
        else:
            print("DATABASE SEED: All config keys already present, skipping.")
            
    except Exception as e:
        print(f"DATABASE CHECK: FAILED! Could not connect to MongoDB.")
        print(f"ERROR: {e}")
    print("------------------------------------------------------------")
    yield
    # Shutdown: Clean up if needed
    pass

def create_app() -> FastAPI:
    app = FastAPI(title="Lead Engine API", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(leads_router, prefix="/api")
    app.include_router(config_router, prefix="/api")
    app.include_router(scheduler_router, prefix="/api")
    return app

app = create_app()
