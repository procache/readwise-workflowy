#!/usr/bin/env python3
"""
Readwise to Workflowy Sync Script (using wfapi library)

This script exports highlights with the "todo" tag from Readwise
and imports them into Workflowy using the wfapi Python library.

This version is more reliable than direct API calls.
"""

import os
import sys
from typing import List, Dict
from dotenv import load_dotenv

try:
    import requests
except ImportError:
    print("Error: requests library not installed")
    print("Run: pip install requests")
    sys.exit(1)

try:
    from wfapi import Workflowy
except ImportError:
    print("Error: wfapi library not installed")
    print("Run: pip install wfapi")
    sys.exit(1)


class ReadwiseClient:
    """Client for interacting with Readwise API."""

    BASE_URL = "https://readwise.io/api/v2"

    def __init__(self, api_token: str):
        """
        Initialize Readwise client.

        Args:
            api_token: Readwise API token from https://readwise.io/access_token
        """
        self.api_token = api_token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Token {api_token}"
        })

    def validate_token(self) -> bool:
        """Validate the API token."""
        try:
            response = self.session.get(f"{self.BASE_URL}/auth/")
            return response.status_code == 204
        except requests.RequestException as e:
            print(f"Error validating Readwise token: {e}")
            return False

    def get_highlights_with_tag(self, tag: str = "todo") -> List[Dict]:
        """
        Fetch all highlights with a specific tag.

        Args:
            tag: Tag name to filter by (default: "todo")

        Returns:
            List of highlight dictionaries
        """
        highlights = []
        url = f"{self.BASE_URL}/highlights/"

        print(f"Fetching highlights with tag '{tag}' from Readwise...")

        while url:
            try:
                response = self.session.get(url)
                response.raise_for_status()
                data = response.json()

                # Filter highlights that have the specified tag
                for highlight in data.get("results", []):
                    tags = highlight.get("tags", [])
                    tag_names = [t.get("name", "").lower() for t in tags]

                    if tag.lower() in tag_names:
                        highlights.append(highlight)

                # Check for next page
                url = data.get("next")

            except requests.RequestException as e:
                print(f"Error fetching highlights: {e}")
                break

        print(f"Found {len(highlights)} highlights with tag '{tag}'")
        return highlights


class WorkflowyWFAPIClient:
    """Client for interacting with Workflowy using wfapi library."""

    def __init__(self, username: str, password: str):
        """
        Initialize Workflowy client using wfapi.

        Args:
            username: Workflowy username/email
            password: Workflowy password
        """
        try:
            print("Connecting to Workflowy...")
            self.wf = Workflowy(username=username, password=password)
            print("✓ Successfully connected to Workflowy")
        except Exception as e:
            print(f"Error connecting to Workflowy: {e}")
            raise

    def create_items_from_highlights(self, highlights: List[Dict]) -> int:
        """
        Create Workflowy items from Readwise highlights.

        Args:
            highlights: List of highlight dictionaries from Readwise

        Returns:
            Number of successfully created items
        """
        created_count = 0
        errors = []

        print(f"\nCreating {len(highlights)} items in Workflowy...\n")

        for idx, highlight in enumerate(highlights, 1):
            try:
                # Extract highlight information
                text = highlight.get("text", "")
                note = highlight.get("note", "")
                book_title = highlight.get("book_title", "Unknown Source")
                author = highlight.get("author", "")
                url = highlight.get("url", "")

                # Build description with metadata
                description_parts = []
                if book_title:
                    description_parts.append(f"📚 Source: {book_title}")
                if author:
                    description_parts.append(f"✍️ Author: {author}")
                if url:
                    description_parts.append(f"🔗 URL: {url}")
                if note:
                    description_parts.append(f"📝 Note: {note}")

                description = "\n".join(description_parts) if description_parts else None

                # Create node in Workflowy root
                node = self.wf.create(self.wf.root)

                # Set the text content
                self.wf.edit(node, text)

                # Add description if we have metadata
                if description:
                    self.wf.edit(node, description=description)

                created_count += 1
                print(f"  [{idx}/{len(highlights)}] ✓ Created: {text[:60]}...")

            except Exception as e:
                error_info = {
                    "index": idx,
                    "text": text[:60] if text else "No text",
                    "error": str(e)
                }
                errors.append(error_info)
                print(f"  [{idx}/{len(highlights)}] ✗ Failed: {text[:60] if text else 'No text'}...")

                # Show detailed error for first 3 failures
                if len(errors) <= 3:
                    print(f"      Error: {str(e)}")

        print(f"\n{'='*70}")
        print(f"Successfully created {created_count}/{len(highlights)} items")

        if errors:
            print(f"\n{len(errors)} items failed. First few errors:")
            for error in errors[:5]:
                print(f"  - Item {error['index']}: {error['text']}")
                print(f"    Error: {error['error']}")

        print(f"{'='*70}\n")

        return created_count


def main():
    """Main function to sync Readwise highlights to Workflowy."""

    # Load environment variables from .env file
    load_dotenv()

    # Load API credentials from environment variables
    readwise_token = os.getenv("READWISE_API_TOKEN")
    workflowy_username = os.getenv("WORKFLOWY_USERNAME")
    workflowy_password = os.getenv("WORKFLOWY_PASSWORD")

    # Validate credentials
    if not readwise_token:
        print("Error: READWISE_API_TOKEN environment variable not set")
        print("Get your token from: https://readwise.io/access_token")
        sys.exit(1)

    if not workflowy_username or not workflowy_password:
        print("Error: WORKFLOWY_USERNAME and WORKFLOWY_PASSWORD must be set")
        print("\nAdd these to your .env file:")
        print("WORKFLOWY_USERNAME=your_email@example.com")
        print("WORKFLOWY_PASSWORD=your_password")
        sys.exit(1)

    # Initialize Readwise client
    print("Initializing Readwise client...")
    readwise = ReadwiseClient(readwise_token)

    if not readwise.validate_token():
        print("Error: Invalid Readwise API token")
        sys.exit(1)

    print("✓ Readwise authentication successful\n")

    # Initialize Workflowy client (using wfapi)
    try:
        workflowy = WorkflowyWFAPIClient(workflowy_username, workflowy_password)
    except Exception as e:
        print(f"\nFailed to connect to Workflowy: {e}")
        print("\nPlease check your credentials and try again.")
        sys.exit(1)

    # Fetch highlights with "todo" tag
    highlights = readwise.get_highlights_with_tag("todo")

    if not highlights:
        print("No highlights found with 'todo' tag")
        sys.exit(0)

    # Create items in Workflowy
    created_count = workflowy.create_items_from_highlights(highlights)

    print(f"✓ Sync complete! {created_count} items created in Workflowy")


if __name__ == "__main__":
    main()
