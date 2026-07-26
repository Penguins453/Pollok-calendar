#!/usr/bin/env python3

"""Pollok FC Calendar Generator."""

import requests

FIXTURES_URL = "https://www.pollokfc.com/calendar/fixtures-and-results-2026-27/"


def main():
    """Download the Pollok fixtures page."""

    print("⚽ Pollok Calendar Generator")
    print("=" * 40)
    print(f"Downloading {FIXTURES_URL}")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(
            FIXTURES_URL,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        print("✓ Download successful")
        print(f"Status: {response.status_code}")
        print(f"Downloaded: {len(response.text):,} characters")

        print("\nFirst 1000 characters:\n")
        print(response.text[:1000])

    except requests.RequestException as err:
        print(f"✗ Download failed: {err}")


if __name__ == "__main__":
    main()