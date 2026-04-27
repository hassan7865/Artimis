import argparse
import logging
import sys
from src.lead_engine.cli import (
    cli_add_keyword, cli_remove_keyword, cli_add_subreddit,
    cli_list_keywords, cli_list_leads, cli_show_lead, loop_mode
)
from src.lead_engine.engine import run_scan

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def main():
    parser = argparse.ArgumentParser(description="Reddit Lead Generation Bot")
    parser.add_argument("--interval",        type=int,  help="Run in loop mode every N seconds")
    parser.add_argument("--add-keyword",     type=str,  help="Add a keyword phrase to monitor")
    parser.add_argument("--remove-keyword",  type=str,  help="Deactivate a keyword phrase")
    parser.add_argument("--add-subreddit",   type=str,  help="Add a subreddit to monitor")
    parser.add_argument("--list-keywords",   action="store_true", help="Show all keywords")
    parser.add_argument("--list-leads",      action="store_true", help="Show recent leads")
    parser.add_argument("--show-lead",       type=str,  help="Show full detail for a lead")
    parser.add_argument("--scan",            action="store_true", help="Run a manual scan immediately")
    
    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    if args.add_keyword:
        cli_add_keyword(args.add_keyword); return
    if args.remove_keyword:
        cli_remove_keyword(args.remove_keyword); return
    if args.add_subreddit:
        cli_add_subreddit(args.add_subreddit); return
    if args.list_keywords:
        cli_list_keywords(); return
    if args.list_leads:
        cli_list_leads(); return
    if args.show_lead:
        cli_show_lead(args.show_lead); return
    if args.scan:
        run_scan(); return

    if args.interval:
        loop_mode(args.interval)
    else:
        run_scan()

if __name__ == "__main__":
    main()
