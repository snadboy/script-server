#!/usr/bin/env python3
"""Fetch random quotes from a public API."""

import argparse
import requests


def fetch_quote(category: str = None) -> dict:
    """Fetch a random quote from the API."""
    url = "https://api.quotable.io/random"
    params = {}
    if category:
        params["tags"] = category

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(description="Fetch random quotes")
    parser.add_argument(
        "-c", "--category",
        help="Quote category (e.g., technology, wisdom, humor)"
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=1,
        help="Number of quotes to fetch (default: 1)"
    )
    args = parser.parse_args()

    for i in range(args.count):
        try:
            quote = fetch_quote(args.category)
            print(f"\n\"{quote['content']}\"")
            print(f"  — {quote['author']}")
            if quote.get('tags'):
                print(f"  Tags: {', '.join(quote['tags'])}")
        except requests.RequestException as e:
            print(f"Error fetching quote: {e}")
            break


if __name__ == "__main__":
    main()
