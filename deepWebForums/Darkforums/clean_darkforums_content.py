import json
import re
import html

INPUT_FILE = "darkforums_threads.json"
OUTPUT_FILE = "darkforums_thread_data_cleaned.json"

def clean_content(raw_text: str) -> str:
    # Decode HTML entities
    text = html.unescape(raw_text)

    # Remove unwanted static phrases
    text = re.sub(
        r"(?i)Note: Upgrade your account to see all hidden content on every post without replying\.",
        "",
        text
    )
    # text = re.sub(r"(?i)Hidden Content", "", text)
    text = re.sub(r"(?i)Show Content", "", text)

    # Replace HTML-like elements (optional fallback if not handled)
    text = text.replace("<br>", "\n").replace("&nbsp;", " ")

    # Collapse excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove leading/trailing empty lines
    return text.strip()

def clean_thread_data():
    with open(INPUT_FILE, "r", encoding="utf-8") as infile:
        threads = json.load(infile)

    cleaned_threads = []
    for thread in threads:
        cleaned = thread.copy()
        cleaned["content"] = clean_content(thread.get("content", ""))
        cleaned_threads.append(cleaned)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        json.dump(cleaned_threads, outfile, indent=2, ensure_ascii=False)

    print(f"✅ Cleaned data written to {OUTPUT_FILE} (Total threads: {len(cleaned_threads)})")

if __name__ == "__main__":
    clean_thread_data()
