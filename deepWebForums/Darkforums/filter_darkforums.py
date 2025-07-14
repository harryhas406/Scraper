import json

# Load keywords
with open('/home/cdot/Desktop/scraper/Scrapers/deepWebForums/critical_keywords.json', 'r', encoding='utf-8') as kf:
    keywords = json.load(kf)

# Load threads
with open('/home/cdot/Desktop/scraper/Scrapers/deepWebForums/Darkforums/darkforums_threads.json', 'r', encoding='utf-8') as tf:
    threads = json.load(tf)

# Filter threads
filtered = []
for entry in threads:
    content = entry.get('content', '').lower()
    title = entry.get('title', '').lower()
    if any(keyword.lower() in content or keyword.lower() in title for keyword in keywords):
        filtered.append(entry)

# Output results
with open('/home/cdot/Desktop/scraper/Scrapers/deepWebForums/Darkforums/darkforums_threads_filtered.json', 'w', encoding='utf-8') as out:
    json.dump(filtered, out, indent=2, ensure_ascii=False)

print(f"Filtered {len(filtered)} entries containing critical keywords in content or title.")