from typing import List, Dict, Tuple
import numpy as np
from fastopic import FASTopic
from topmost.preprocessing import Preprocessing
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TopicVideoClassifier:
    """Classifies YouTube videos based on their titles using FASTopic."""

    def __init__(self, num_topics: int = 20):
        self.num_topics = num_topics
        self.preprocessing = Preprocessing(stopwords="English")
        self.model = FASTopic(num_topics=num_topics, preprocessing=self.preprocessing)
        self.topic_keywords = None
        self.doc_topics = None

    def _extract_topics(self, titles: List[str]) -> Tuple[List[List[str]], np.ndarray]:
        """Extract topics from video titles using FASTopic."""
        try:
            topic_words, doc_topic_dist = self.model.fit_transform(titles)
            return topic_words, doc_topic_dist
        except Exception as e:
            logger.error(f"Error in topic extraction: {e}")
            raise

    def analyze_titles(self, titles: List[str]) -> Dict:
        """Analyze video titles and return topic information."""
        if len(titles) < 2:
            logger.warning("Not enough titles for meaningful topic analysis")
            return {
                "topic_distributions": None,
                "topic_keywords": [],
                "dominant_topics": ["Uncategorized"] * len(titles),
            }

        # Extract topics
        self.topic_keywords, self.doc_topics = self._extract_topics(titles)

        # Get dominant topic for each document
        dominant_topics = np.argmax(self.doc_topics, axis=1)

        return {
            "topic_distributions": self.doc_topics,
            "topic_keywords": self.topic_keywords,
            "dominant_topics": [f"Topic_{i}" for i in dominant_topics],
        }

    def visualize_topics(self, output_path: str | Path, top_n: int = 20) -> None:
        """Generate and save topic visualization."""
        if self.topic_keywords is None:
            logger.warning("No topics available for visualization")
            return

        try:
            fig = self.model.visualize_topic_weights(top_n=top_n, height=800)
            fig.write_image(str(Path(output_path) / "topic_visualization.png"))
            logger.info(f"Topic visualization saved to {output_path}")
        except Exception as e:
            logger.error(f"Error generating topic visualization: {e}")
            raise

    def get_video_categories(self, titles: List[str]) -> Dict:
        """Get category information for a list of video titles."""
        analysis = self.analyze_titles(titles)

        return {
            "categories": analysis["dominant_topics"],
            "topic_keywords": analysis["topic_keywords"],
        }
