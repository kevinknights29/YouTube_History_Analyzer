import pytest
import numpy as np
from youtube_history_analyzer.classifier import TopicVideoClassifier


@pytest.fixture
def sample_titles():
    return [
        "Python Programming Tutorial - Basic Concepts",
        "Learn Python in 2024 - Complete Course",
        "Gaming Stream Highlights - Best Moments",
        "Epic Gaming Montage 2024",
        "Latest Tech News and Updates",
        "Technology Review - New Gadgets 2024",
        "Random Vlog - My Daily Life",
        "Personal Update - Life Changes",
    ]


@pytest.fixture
def classifier():
    return TopicVideoClassifier(num_topics=5)


def test_topic_extraction(classifier, sample_titles, tmp_path):
    analysis = classifier.analyze_titles(sample_titles)

    assert analysis["topic_distributions"] is not None
    assert isinstance(analysis["topic_distributions"], np.ndarray)
    assert len(analysis["topic_keywords"]) == 5  # num_topics

    # Test visualization
    classifier.visualize_topics(tmp_path)
    assert (tmp_path / "topic_visualization.png").exists()

    # Print topics for inspection
    print("\nExtracted topics:")
    for i, words in enumerate(analysis["topic_keywords"]):
        print(f"Topic_{i}: {', '.join(words)}")


def test_small_dataset_handling(classifier):
    titles = ["Single Video Title"]
    result = classifier.get_video_categories(titles)

    assert len(result["categories"]) == 1
    assert result["categories"][0] == "Uncategorized"
