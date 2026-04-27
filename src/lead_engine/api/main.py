from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from lead_engine.api.routers.leads import router as leads_router
from lead_engine.api.routers.config import router as config_router
from lead_engine.api.routers.scheduler import router as scheduler_router

from contextlib import asynccontextmanager
from lead_engine.database import get_db

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
        config_count = await db.config.count_documents({})
        if config_count == 0:
            print("DATABASE SEED: Initialising default high-intent targets...")
            
            # Massive coverage: Development, Design, Marketing, Content, Sales, and Consulting
            default_keywords = [
                "hiring", "looking for", "need a developer", "recommend an agency",
                "freelancer needed", "budget for", "build an app", "fix my website",
                "seo help", "manage my ads", "outsource", "quote for", "proposal",
                "shopify expert", "custom solution", "automation help", "app development",
                "ui/ux design", "logo design", "content writer", "copywriting",
                "lead generation", "cold calling", "crm setup", "hubspot expert",
                "wordpress help", "mobile app developer", "mvp development",
                "saas developer", "e-commerce growth", "facebook ads", "google ads",
                "fractional cto", "video editor", "ghostwriter", "marketing strategist"
            ]
            
            default_subreddits = [
                "smallbusiness", "entrepreneur", "startups", "SaaS", "webdev",
                "marketing", "ecommerce", "shopify", "freelance", "digitalmarketing",
                "business", "copywriting", "design", "graphic_design", "webdesign",
                "SEO", "PPC", "SocialMediaMarketing", "workonline", "sideproject"
            ]

            default_prompt = """You are an expert Technical B2B Lead Analyst. 
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
            
            await db.config.insert_many([
                {"key": "keywords", "value": ",".join(default_keywords)},
                {"key": "subreddits", "value": ",".join(default_subreddits)},
                {"key": "ai_prompt", "value": default_prompt}
            ])
            print("DATABASE SEED: SUCCESS! Keywords, Subreddits, and AI Prompt added.")
            
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
