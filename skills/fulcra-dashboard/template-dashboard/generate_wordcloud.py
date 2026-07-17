#!/usr/bin/env python3
"""
Example Backend Visualization Script:
Generates a Word Cloud from Fulcra Annotation note fields.

Requirements:
    pip install wordcloud matplotlib
"""

import sys
import json
from pathlib import Path
try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
except ImportError:
    print("Error: Missing required packages. Run: pip install wordcloud matplotlib")
    sys.exit(1)

def generate_wordcloud_from_jsonl(file_path, output_path="wordcloud.png"):
    text_corpus = ""
    
    # Read the Fulcra JSONL data
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                if 'note' in record and record['note']:
                    text_corpus += " " + record['note']
            except json.JSONDecodeError:
                continue

    if not text_corpus.strip():
        print("No 'note' data found in the provided JSONL to generate a word cloud.")
        return

    # Generate the Word Cloud
    print("Generating Word Cloud...")
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='rgba(255, 255, 255, 0)', # Transparent background
        mode="RGBA",
        colormap='cool', # Fits well with dark/modern themes
        max_words=100
    ).generate(text_corpus)

    # Save to file
    wordcloud.to_file(output_path)
    print(f"✅ Word Cloud successfully saved to {output_path}")
    print("You can now reference this image in your dashboard's index.html: <img src=\"wordcloud.png\">")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_wordcloud.py <path_to_fulcra_data.jsonl>")
        sys.exit(1)
        
    input_jsonl = sys.argv[1]
    output_image = "wordcloud.png"
    if len(sys.argv) > 2:
        output_image = sys.argv[2]
        
    generate_wordcloud_from_jsonl(input_jsonl, output_image)
