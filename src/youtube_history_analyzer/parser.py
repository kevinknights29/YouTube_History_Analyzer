from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import logging
from typing import Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class YouTubeHistoryParser:
    """Parser for YouTube watch history HTML files exported from Google Takeout."""

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.soup = None

    def _load_html(self) -> None:
        """Load and parse HTML file using BeautifulSoup."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.soup = BeautifulSoup(file, "html.parser")
                logger.info(f"Successfully loaded {self.file_path}")
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            raise

    def _parse_watch_entry(self, entry) -> Dict:
        """Parse a single watch history entry."""
        try:
            # First verify we have a valid entry
            if not entry:
                logger.warning("Empty entry provided to _parse_watch_entry")
                return None

            # Find the content cell with the correct class
            # Note: Using find with partial class match
            content = entry.find(
                "div",
                class_=lambda x: x
                and all(
                    c in x
                    for c in [
                        "content-cell",
                        "mdl-cell--6-col",
                        "mdl-typography--body-1",
                    ]
                ),
            )

            if not content:
                logger.debug("Could not find content cell")
                return None

            # Extract video information
            links = content.find_all("a")
            if len(links) < 2:
                logger.debug(f"Not enough links found in entry: {len(links)}")
                return None

            # Extract text and clean it
            video_link = links[0]
            channel_link = links[1]

            # Get date from the text content
            text_content = content.get_text(separator="\n", strip=True)
            date_text = text_content.split("\n")[-1]

            # Parse date
            try:
                date = datetime.strptime(date_text, "%b %d, %Y, %I:%M:%S %p %Z")
            except ValueError as e:
                logger.warning(f"Could not parse date '{date_text}': {e}")
                return None

            return {
                "video": video_link.text.strip(),
                "video_url": video_link["href"],
                "channel": channel_link.text.strip(),
                "channel_url": channel_link["href"],
                "date": date,
            }
        except Exception as e:
            logger.warning(f"Error parsing entry: {e}")
            return None

    def parse_history(self) -> pd.DataFrame:
        """Parse the entire watch history and return as DataFrame."""
        if not self.soup:
            self._load_html()

        entries = []
        watch_entries = self.soup.find_all(
            "div", class_="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp"
        )

        logger.info(f"Found {len(watch_entries)} potential watch entries")

        for entry in watch_entries:
            parsed_entry = self._parse_watch_entry(entry)
            if parsed_entry:
                entries.append(parsed_entry)

        logger.info(f"Successfully parsed {len(entries)} watch history entries")

        if not entries:
            logger.warning("No entries were successfully parsed")
            return pd.DataFrame(
                columns=["video", "video_url", "channel", "channel_url", "date"]
            )

        return pd.DataFrame(entries)
