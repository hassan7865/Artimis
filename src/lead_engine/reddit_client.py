import requests
import logging
from datetime import datetime, timezone

log = logging.getLogger("leadgen.reddit")

HEADERS = {
    "User-Agent": "reddit-leadgen-bot/1.0 (contact: your@email.com)"
}

def fetch_subreddit_posts(subreddit: str, limit: int = 25) -> list[dict]:
    """
    Fetch newest posts from a subreddit using the public .json endpoint.
    Returns a list of simplified post dicts.
    """
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"
    try:
        log.info("Fetching subreddit feed: r/%s limit=%d url=%s", subreddit, limit, url)
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        log.info("Reddit response received: r/%s status=%d", subreddit, resp.status_code)
        data = resp.json()
        posts = []
        children = data.get("data", {}).get("children", [])
        for index, child in enumerate(children, start=1):
            p = child["data"]
            post = {
                "post_id":   p["id"],
                "subreddit": subreddit,
                "title":     p.get("title", ""),
                "body":      p.get("selftext", "")[:2000],
                "author":    p.get("author", "[deleted]"),
                "url":       f"https://reddit.com{p.get('permalink', '')}",
                "upvotes":   p.get("ups", 0),
                "created_utc": p.get("created_utc", 0),
            }
            posts.append(post)
            body_preview = post["body"].replace("\n", " ").strip()[:140]
            created_at = datetime.fromtimestamp(post["created_utc"], tz=timezone.utc)
            log.info(
                "Fetched post %d/%d from r/%s: id=%s author=u/%s upvotes=%d created_at=%s title=%r body_preview=%r url=%s",
                index,
                len(children),
                subreddit,
                post["post_id"],
                post["author"],
                post["upvotes"],
                created_at.isoformat(),
                post["title"][:160],
                body_preview,
                post["url"],
            )
        log.info("  r/%-20s  fetched %d posts", subreddit, len(posts))
        return posts
    except Exception as exc:
        log.warning("  r/%-20s  fetch failed: %s", subreddit, exc)
        return []
