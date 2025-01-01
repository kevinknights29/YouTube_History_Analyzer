import logging
from .parser import YouTubeHistoryParser

logger = logging.getLogger(__name__)


def process_watch_history(input_path: str, output_path: str) -> None:
    """Process watch history from HTML to CSV."""
    try:
        # Parse watch history
        parser = YouTubeHistoryParser(input_path)
        df = parser.parse_history()

        # Export to CSV
        df.to_csv(output_path, index=False)
        logger.info(f"Successfully exported watch history to {output_path}")

    except Exception as e:
        logger.error(f"Error processing watch history: {e}")
        raise
