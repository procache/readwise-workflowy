#!/usr/bin/env python3
"""
Readwise to Workflowy Sync Script

This script exports highlights with the "todo" tag from Readwise
and imports them into Workflowy.
"""

import os
import sys
import requests
from typing import List, Dict, Optional
from datetime import datetime
import json
from dotenv import load_dotenv


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


class WorkflowyClient:
    """Client for interacting with Workflowy API."""

    BASE_URL = "https://workflowy.com/api"

    def __init__(self, session_id: Optional[str] = None, bearer_token: Optional[str] = None):
        """
        Initialize Workflowy client.

        Args:
            session_id: Workflowy session ID cookie (legacy auth)
            bearer_token: Workflowy Bearer token (OAuth 2.0)
        """
        self.session = requests.Session()

        if bearer_token:
            self.session.headers.update({
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "application/json"
            })
        elif session_id:
            self.session.cookies.set("sessionid", session_id)
            self.session.headers.update({
                "Content-Type": "application/json"
            })
        else:
            raise ValueError("Either session_id or bearer_token must be provided")

    def create_item(self, name: str, parent_id: Optional[str] = None, note: Optional[str] = None) -> bool:
        """
        Create a new item in Workflowy.

        Args:
            name: The text content of the item
            parent_id: ID of parent item (None for root level)
            note: Optional note to attach to the item

        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {
                "name": name
            }

            if parent_id:
                payload["parentid"] = parent_id

            if note:
                payload["note"] = note

            response = self.session.post(
                f"{self.BASE_URL}/create",
                json=payload
            )
            response.raise_for_status()
            return True

        except requests.RequestException as e:
            print(f"Error creating Workflowy item: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return False

    def bulk_create_items(self, highlights: List[Dict]) -> int:
        """
        Create multiple items from Readwise highlights.

        Args:
            highlights: List of highlight dictionaries from Readwise

        Returns:
            Number of successfully created items
        """
        created_count = 0

        print(f"Creating {len(highlights)} items in Workflowy...")

        for highlight in highlights:
            # Extract highlight information
            text = highlight.get("text", "")
            note = highlight.get("note", "")
            book_title = highlight.get("book_title", "Unknown Source")
            author = highlight.get("author", "")
            url = highlight.get("url", "")

            # Format the item text
            item_text = f"{text}"

            # Build a comprehensive note
            note_parts = []
            if book_title:
                note_parts.append(f"Source: {book_title}")
            if author:
                note_parts.append(f"Author: {author}")
            if url:
                note_parts.append(f"URL: {url}")
            if note:
                note_parts.append(f"Note: {note}")

            item_note = "\n".join(note_parts) if note_parts else None

            # Create the item
            if self.create_item(item_text, note=item_note):
                created_count += 1
                print(f"  ✓ Created: {item_text[:60]}...")
            else:
                print(f"  ✗ Failed: {item_text[:60]}...")

        print(f"\nSuccessfully created {created_count}/{len(highlights)} items")
        return created_count


def main():
    """Main function to sync Readwise highlights to Workflowy."""

    # Load environment variables from .env file
    load_dotenv()

    # Load API credentials from environment variables
    readwise_token = os.getenv("READWISE_API_TOKEN")
    workflowy_bearer_token = os.getenv("WORKFLOWY_BEARER_TOKEN")
    workflowy_session_id = os.getenv("WORKFLOWY_SESSION_ID")

    # Validate credentials
    if not readwise_token:
        print("Error: READWISE_API_TOKEN environment variable not set")
        print("Get your token from: https://readwise.io/access_token")
        sys.exit(1)

    if not workflowy_bearer_token and not workflowy_session_id:
        print("Error: Either WORKFLOWY_BEARER_TOKEN or WORKFLOWY_SESSION_ID must be set")
        sys.exit(1)

    # Initialize clients
    print("Initializing Readwise client...")
    readwise = ReadwiseClient(readwise_token)

    if not readwise.validate_token():
        print("Error: Invalid Readwise API token")
        sys.exit(1)

    print("✓ Readwise authentication successful\n")

    print("Initializing Workflowy client...")
    workflowy = WorkflowyClient(
        session_id=workflowy_session_id,
        bearer_token=workflowy_bearer_token
    )
    print("✓ Workflowy client initialized\n")

    # Fetch highlights with "todo" tag
    highlights = readwise.get_highlights_with_tag("todo")

    if not highlights:
        print("No highlights found with 'todo' tag")
        sys.exit(0)

    # Create items in Workflowy
    created_count = workflowy.bulk_create_items(highlights)

    print(f"\n✓ Sync complete! {created_count} items created in Workflowy")


if __name__ == "__main__":
    main()
