import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

url = 'https://sam.mat.ethz.ch/2025/05/30/materials-colloquium-2025-june-5th/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

title = soup.select_one('article h1').text.strip()
speakers = soup.select_one('article p:nth-of-type(2)').text.strip()
loc_time = soup.select_one('article p:nth-of-type(1)').text.strip()

# Extract year
year_match = re.search(r'(\d{4})', title)
year = year_match.group(1) if year_match else "Unknown"

# Extract month and day after comma
md_match = re.search(r',\s*(\w+ \d{1,2}(?:st|nd|rd|th)?)', title)
md_str = md_match.group(1) if md_match else None

if md_str and year != "Unknown":
    md_clean = re.sub(r'(st|nd|rd|th)', '', md_str)
    date_str = f"{md_clean} {year}"
else:
    date_str = "Unknown"

try:
    date_obj = datetime.strptime(date_str, '%B %d %Y')
    date = date_obj.strftime('%Y-%m-%d')
except Exception as e:
    print(f"Date parsing error: {e}")
    date = "Unknown"

time_match = re.search(r'(\d{1,2}:\d{2})', loc_time)
time = time_match.group(1) if time_match else "Unknown"
location = loc_time.split(',')[0].strip()

event = {
    "date": date,
    "time": time,
    "location": location,
    "title": title,
    "speaker": speakers,
    "info": url
}

print(json.dumps(event, indent=2))
