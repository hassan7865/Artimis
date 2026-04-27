import requests
import logging

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
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        posts = []
        for child in data.get("data", {}).get("children", []):
            p = child["data"]
            posts.append({
                "post_id":   p["id"],
                "subreddit": subreddit,
                "title":     p.get("title", ""),
                "body":      p.get("selftext", "")[:2000],
                "author":    p.get("author", "[deleted]"),
                "url":       f"https://reddit.com{p.get('permalink', '')}",
                "upvotes":   p.get("ups", 0),
                "created_utc": p.get("created_utc", 0),
            })
        log.info("  r/%-20s  fetched %d posts", subreddit, len(posts))
        return posts
    except Exception as exc:
        log.warning("  r/%-20s  fetch failed: %s", subreddit, exc)
        return []
