import time
import json
import logging
import asyncio
from datetime import datetime
from .config import CONFIG
from .database import (
    get_active_subreddits, get_active_keywords,
    save_lead, log_scan, mark_notified, save_ai_log,
    is_post_processed, mark_post_processed
)
from .reddit_client import fetch_subreddit_posts
from .analyzer import detect_intents, keyword_score, analyse_with_gpt
from .notifiers import notify_slack, notify_email

log = logging.getLogger("leadgen.engine")

async def run_scan():
    """One full scan cycle: fetch → detect → score → store → notify."""
    start = time.time()
    min_post_age_seconds = CONFIG["MIN_POST_AGE_MINUTES"] * 60
    max_post_age_seconds = CONFIG["MAX_POST_AGE_MINUTES"] * 60

    subreddits = await get_active_subreddits()
    keywords   = await get_active_keywords()
    log.info("═" * 60)
    log.info("SCAN STARTED  %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log.info("Monitoring:   %s", ", ".join(f"r/{s}" for s in subreddits))
    log.info("Keywords:     %d active", len(keywords))
    log.info(
        "Post age:     %d-%d minutes old",
        CONFIG["MIN_POST_AGE_MINUTES"],
        CONFIG["MAX_POST_AGE_MINUTES"],
    )
    log.info("═" * 60)

    total_fetched  = 0
    total_new      = 0
    total_leads    = 0
    total_ai_calls = 0
    skipped_processed = 0
    skipped_too_new = 0
    skipped_too_old = 0
    processed_posts = 0

    for subreddit in subreddits:
        # Fetching posts is still synchronous for now (requests), but we wrap it
        posts = fetch_subreddit_posts(subreddit, limit=CONFIG["POSTS_PER_SUBREDDIT"])
        await asyncio.sleep(CONFIG["REQUEST_DELAY_SEC"])

        for post in posts:
            total_fetched += 1
            post_age_seconds = max(0, time.time() - post["created_utc"])
            post_age_minutes = round(post_age_seconds / 60, 1)

            if await is_post_processed(post["post_id"]):
                skipped_processed += 1
                log.info(
                    "  Skipping already processed post: %s age=%s min",
                    post["post_id"],
                    post_age_minutes,
                )
                continue

            if post_age_seconds < min_post_age_seconds:
                skipped_too_new += 1
                log.info(
                    "  Skipping post %s from r/%s: too new (%s min old)",
                    post["post_id"],
                    subreddit,
                    post_age_minutes,
                )
                continue

            if post_age_seconds > max_post_age_seconds:
                skipped_too_old += 1
                log.info(
                    "  Skipping post %s from r/%s: too old (%s min old)",
                    post["post_id"],
                    subreddit,
                    post_age_minutes,
                )
                continue

            try:
                total_new += 1
                processed_posts += 1
                log.info(
                    "  Processing eligible post: %s r/%s age=%s min title=%r",
                    post["post_id"],
                    subreddit,
                    post_age_minutes,
                    post["title"][:120],
                )

                full_text = f"{post['title']} {post['body']}"
                intents, matched_kws = detect_intents(full_text, keywords)
                pre_score = keyword_score(matched_kws, post["upvotes"], intents)

                if pre_score < CONFIG["MIN_PRESCORE_FOR_AI"]:
                    await mark_post_processed(post["post_id"])
                    continue

                log.info("  Potential lead [pre=%d]: r/%s — %s",
                         pre_score, subreddit, post["title"][:65])

                ai = await analyse_with_gpt(post, intents, matched_kws)
                total_ai_calls += 1
                
                lead_record = {
                    "post_id":          post["post_id"],
                    "subreddit":        post["subreddit"],
                    "title":            post["title"],
                    "body":             post["body"],
                    "author":           post["author"],
                    "url":              post["url"],
                    "upvotes":          post["upvotes"],
                    "score":            ai["score"],
                    "intents":          json.dumps(intents),
                    "matched_keywords": json.dumps(matched_kws),
                    "ai_analysis":      ai["analysis"],
                    "ai_outreach":      ai["outreach"],
                }
                
                if ai["score"] >= 70:
                    await save_lead(lead_record)
                    total_leads += 1

                    if ai["score"] >= CONFIG["MIN_SCORE_TO_NOTIFY"]:
                        notify_slack(lead_record)
                        notify_email(lead_record)
                        await mark_notified(post["post_id"])
                else:
                    log.info("  Lead discarded (Score %d below 70): %s", ai["score"], post["post_id"])
                
                # Save AI Logs
                if "_log" in ai:
                    await save_ai_log(
                        post["post_id"], 
                        ai["_log"]["input"], 
                        ai["_log"]["output"], 
                        ai["_log"]["tokens"]
                    )

                # Mark processed only after pipeline succeeds.
                await mark_post_processed(post["post_id"])
            except Exception:
                log.exception("Failed to process post %s", post.get("post_id"))

    duration = round(time.time() - start, 2)
    await log_scan(
        total_new,
        total_leads,
        duration,
        total_fetched,
        processed_posts,
        skipped_processed,
        skipped_too_new,
        skipped_too_old,
    )

    log.info("─" * 60)
    log.info("SCAN COMPLETE in %ss", duration)
    log.info(
        "Fetched=%d Processed=%d Skipped(processed=%d too_new=%d too_old=%d) Leads=%d AI calls=%d",
        total_fetched,
        processed_posts,
        skipped_processed,
        skipped_too_new,
        skipped_too_old,
        total_leads,
        total_ai_calls,
    )
    log.info("─" * 60)
    return total_new, total_leads
