import pytest
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from pathlib import Path

from youtube_history_analyzer.parser import YouTubeHistoryParser
from youtube_history_analyzer.cli import process_watch_history


@pytest.fixture
def sample_html_content():
    """Create a sample HTML content that exactly matches the expected structure"""
    return """<!DOCTYPE html>
    <html>
    <body>
    <div class="mdl-grid">
        <div class="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp">
            <div class="mdl-grid">
                <div class="header-cell mdl-cell mdl-cell--12-col">
                    <p class="mdl-typography--title">YouTube</p>
                </div>
                <div class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1">
                    Watched <a href="https://www.youtube.com/watch?v=123">Test Video</a><br>
                    <a href="https://www.youtube.com/channel/456">Test Channel</a><br>
                    Feb 23, 2024, 7:36:45 PM EST
                </div>
                <div class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1 mdl-typography--text-right">
                </div>
            </div>
        </div>
    </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_file(tmp_path, sample_html_content):
    file_path = tmp_path / "test-watch-history.html"
    file_path.write_text(sample_html_content)
    return file_path


@pytest.fixture
def parser(sample_html_file):
    return YouTubeHistoryParser(sample_html_file)


def test_parser_initialization(parser):
    """Test parser initialization"""
    assert isinstance(parser.file_path, Path)
    assert parser.soup is None


def test_load_html(parser):
    """Test HTML loading functionality"""
    parser._load_html()
    assert parser.soup is not None
    assert isinstance(parser.soup, BeautifulSoup)


def test_parse_watch_entry(parser):
    """Test parsing of a single watch entry"""
    parser._load_html()

    # Find the entry
    entry = parser.soup.find(
        "div", class_="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp"
    )
    assert entry is not None, "Could not find the outer cell div"

    # Debug print
    print("\nTesting entry structure:")
    print(entry.prettify())

    result = parser._parse_watch_entry(entry)

    # Detailed assertion messages
    assert result is not None, "Parser returned None instead of a valid entry"

    expected_video = "Test Video"
    assert (
        result["video"] == expected_video
    ), f"Expected video title '{expected_video}', got '{result['video']}'"

    expected_url = "https://www.youtube.com/watch?v=123"
    assert (
        result["video_url"] == expected_url
    ), f"Expected video URL '{expected_url}', got '{result['video_url']}'"

    expected_channel = "Test Channel"
    assert (
        result["channel"] == expected_channel
    ), f"Expected channel '{expected_channel}', got '{result['channel']}'"

    expected_channel_url = "https://www.youtube.com/channel/456"
    assert (
        result["channel_url"] == expected_channel_url
    ), f"Expected channel URL '{expected_channel_url}', got '{result['channel_url']}'"

    assert isinstance(result["date"], datetime), "Date should be a datetime object"


def test_parse_history(parser):
    """Test parsing of complete history"""
    df = parser.parse_history()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1  # Should have one entry from our sample
    assert list(df.columns) == [
        "video",
        "video_url",
        "channel",
        "channel_url",
        "date",
        "category",
    ]


def test_parse_history_with_real_file():
    """Test with the actual watch-history.html file"""
    parser = YouTubeHistoryParser("data/input/watch-history.html")
    df = parser.parse_history()

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0  # Should have entries
    print(f"\nNumber of entries found: {len(df)}")  # Debug print

    # Print first few entries for debugging
    if len(df) > 0:
        print("\nFirst entry:")
        print(df.iloc[0])


def test_invalid_entry_structure(tmp_path):
    """Test handling of malformed HTML entries"""
    invalid_html = """
    <div class="mdl-grid">
        <div class="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp">
            <div class="mdl-grid">
                <div class="content-cell mdl-cell--6-col">
                    Invalid structure
                </div>
            </div>
        </div>
    </div>
    """
    file_path = tmp_path / "invalid-watch-history.html"
    file_path.write_text(invalid_html)

    parser = YouTubeHistoryParser(file_path)
    df = parser.parse_history()
    assert len(df) == 0  # Should handle invalid entries gracefully


def test_debug_soup_structure(sample_html_file):
    """Debug test to print out the soup structure"""
    parser = YouTubeHistoryParser(sample_html_file)
    parser._load_html()

    # Print out all outer-cell divs
    outer_cells = parser.soup.find_all("div", class_="outer-cell mdl-cell--12-col")
    print(f"\nNumber of outer cells found: {len(outer_cells)}")

    # Print out all content cells
    content_cells = parser.soup.find_all("div", class_="content-cell mdl-cell--6-col")
    print(f"Number of content cells found: {len(content_cells)}")

    # If we find cells, print the first one for inspection
    if content_cells:
        print("\nFirst content cell structure:")
        print(content_cells[0].prettify())


def test_cli_process_watch_history(tmp_path, sample_html_content):
    """Test the CLI processing function"""
    input_file = tmp_path / "test-watch-history.html"
    output_file = tmp_path / "output.csv"

    input_file.write_text(sample_html_content)

    process_watch_history(str(input_file), str(output_file))

    assert output_file.exists()
    df = pd.read_csv(output_file)
    assert len(df) == 1


def test_debug_html_structure(parser):
    """Debug test to understand HTML structure"""
    parser._load_html()

    # Find all relevant elements
    outer_cells = parser.soup.find_all(
        "div", class_="outer-cell mdl-cell mdl-cell--12-col mdl-shadow--2dp"
    )
    content_cells = parser.soup.find_all(
        "div", class_=lambda x: x and "content-cell" in x and "mdl-cell--6-col" in x
    )

    print("\nStructure Analysis:")
    print(f"Outer cells found: {len(outer_cells)}")
    print(f"Content cells found: {len(content_cells)}")

    if outer_cells:
        print("\nFirst outer cell classes:", outer_cells[0].get("class"))
    if content_cells:
        print("\nFirst content cell classes:", content_cells[0].get("class"))
        print("\nFirst content cell text:", content_cells[0].get_text(strip=True))
