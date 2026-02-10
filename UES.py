import requests
import requests.exceptions
import urllib.parse
from bs4 import BeautifulSoup
from collections import deque
import re

# 1. Setup Input and Queue
user_url = input('[+] Enter Target URL To Scan: ')
urls = deque([user_url])

scraped_urls = set()
emails = set()

# To keep the crawler from leaving the website you targeted
target_domain = urllib.parse.urlsplit(user_url).netloc

count = 0

print("-" * 50)
try:
    while len(urls):
        if count >= 100: # Limit to 100 pages
            break
            
        url = urls.popleft()
        
        # Skip if we have already crawled this specific page
        if url in scraped_urls:
            continue
            
        count += 1
        scraped_urls.add(url)

        print(f'[{count}] Processing {url}')
        
        try:
            # Headers make the request look like it's coming from a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            continue

        # 2. Extract Emails using Regex
        # Added a slightly more robust regex pattern
        new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
        emails.update(new_emails)

        # 3. Find and Process Links
        soup = BeautifulSoup(response.text, features="lxml")

        for anchor in soup.find_all("a"):
            link = anchor.attrs['href'] if 'href' in anchor.attrs else ''
            
            # Convert relative links (like /about) to absolute (http://site.com/about)
            link = urllib.parse.urljoin(url, link)

            # Domain check: Only add the link if it belongs to the same website
            if target_domain in link and link not in scraped_urls and link not in urls:
                urls.append(link)

except KeyboardInterrupt:
    print('\n[-] Closing early...')

# 4. Final Results
print("-" * 50)
print(f"\n[!] Process Complete. Found {len(emails)} unique emails:\n")

if emails:
    for mail in emails:
        print(f"  -> {mail}")
else:
    print("  No emails found. (The site may use JavaScript to hide them or have no emails listed.)")
