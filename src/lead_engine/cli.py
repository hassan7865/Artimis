import logging
import time
from .database import get_db, init_db
from .engine import run_scan

log = logging.getLogger("leadgen.cli")

def cli_add_keyword(phrase: str):
    conn = get_db(); init_db(conn)
    conn.execute("INSERT OR IGNORE INTO keywords (phrase) VALUES (?)", (phrase.lower(),))
    conn.commit(); conn.close()
    print(f"✅  Keyword added: '{phrase}'")

def cli_remove_keyword(phrase: str):
    conn = get_db(); init_db(conn)
    conn.execute("UPDATE keywords SET active = 0 WHERE phrase = ?", (phrase.lower(),))
    conn.commit(); conn.close()
    print(f"🗑️   Keyword deactivated: '{phrase}'")

def cli_add_subreddit(name: str):
    conn = get_db(); init_db(conn)
    name = name.lstrip("r/")
    conn.execute("INSERT OR IGNORE INTO subreddits (name) VALUES (?)", (name,))
    conn.commit(); conn.close()
    print(f"✅  Subreddit added: r/{name}")

def cli_list_keywords():
    conn = get_db(); init_db(conn)
    rows = conn.execute("SELECT phrase, active, added_at FROM keywords ORDER BY active DESC, phrase").fetchall()
    conn.close()
    print(f"\n{'PHRASE':<45} {'ACTIVE':<8} {'ADDED'}")
    print("─" * 70)
    for r in rows:
        status = "yes" if r["active"] else "no"
        print(f"{r['phrase']:<45} {status:<8} {r['added_at']}")

def cli_list_leads(limit: int = 20):
    conn = get_db(); init_db(conn)
    rows = conn.execute("""
        SELECT post_id, subreddit, score, title, status, found_at
        FROM leads ORDER BY score DESC, found_at DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    print(f"\n{'SCORE':<7} {'SUB':<16} {'STATUS':<12} {'TITLE':<50}")
    print("─" * 110)
    for r in rows:
        print(f"{r['score']:<7} r/{r['subreddit']:<14} {r['status']:<12} {r['title'][:48]:<50}")

def cli_show_lead(post_id: str):
    conn = get_db(); init_db(conn)
    row = conn.execute("SELECT * FROM leads WHERE post_id = ?", (post_id,)).fetchone()
    conn.close()
    if not row:
        print(f"Lead not found: {post_id}")
        return
    print(f"\n━━━ LEAD DETAIL: {row['post_id']} ━━━")
    print(f"Title:     {row['title']}")
    print(f"Sub:       r/{row['subreddit']} | Score: {row['score']}")
    print(f"URL:       {row['url']}")
    print(f"Analysis:  {row['ai_analysis']}")
    print(f"Outreach:  {row['ai_outreach']}")

def loop_mode(interval: int):
    log.info("Loop mode: scanning every %d seconds. Press Ctrl+C to stop.", interval)
    while True:
        try:
            run_scan()
        except KeyboardInterrupt:
            break
        except Exception as e:
            log.error("Scan error: %s", e)
        time.sleep(interval)
