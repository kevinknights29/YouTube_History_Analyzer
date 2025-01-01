from youtube_history_analyzer.cli import process_watch_history

if __name__ == "__main__":
    input_file = "data/input/watch-history.html"
    output_file = "data/output/watch-history.csv"

    process_watch_history(input_file, output_file)
