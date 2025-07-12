import requests
import json
import re

API_URL = "https://idapps.ethz.ch/pcm-pub-services/v2/entries?filters[0].e-types=1,2,3,6,7,9,10,16,19,20,101,221,301,401,521&filters[0].max-till-start=120&filters[0].min-till-end=0&filters[0].org-units=02140wd&rs-first=0&rs-size=9999&lang=en&client-id=wcms&comp-ext=true&filters[0].cals=1"
WEBSITE_PREFIX = "https://ee.ethz.ch/news-and-events/events/details"

def make_slug(title):
    # Lowercase, remove non-alphanumeric except spaces, then replace spaces with hyphens
    slug = title.lower().strip()
    slug = re.sub(r'[^a-z0-9 ]+', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    return slug

def event_info_url(title, event_id):
    slug = make_slug(title)
    return f"{WEBSITE_PREFIX}.{slug}.{event_id}.html"

def get_speaker(function_owner_array):
    speakers = []
    for p in function_owner_array:
        if p.get("function-desc", "").lower() == "speaker":
            name = ""
            if p.get("title-desc"):
                name += p["title-desc"] + " "
            name += p.get("first-name", "").strip() + " " + p.get("last-name", "").strip()
            name = name.strip()
            if name:
                speakers.append(name)
    return ", ".join(speakers)

def main():
    response = requests.get(API_URL)
    data = response.json()
    entries = data.get("entry-array", [])

    seminars = []
    for entry in entries:
        if entry.get("classification", {}).get("entry-type-desc") != "Seminar":
            continue  # skip non-seminars

        date_time = entry.get("date-time-indication", {}).get("date-with-times-array", [{}])[0]
        date = date_time.get("date", "")
        time = date_time.get("time-from", "")

        # Location
        location_data = entry.get("location", {}).get("internal", {})
        location_parts = [location_data.get("building",""), location_data.get("floor",""), location_data.get("room","")]
        location = "/".join([part for part in location_parts if part]).strip("/")

        # Title
        title = entry.get("content", {}).get("title", "")

        # Speaker(s)
        speaker = get_speaker(entry.get("function-owner-array", []))

        # Info: build detail page URL
        event_id = entry.get("id")
        info = event_info_url(title, event_id) if title and event_id else ""

        seminars.append({
            "date": date,
            "time": time,
            "location": location,
            "title": title,
            "speaker": speaker,
            "info": info
        })

    print(json.dumps(seminars, indent=2))

if __name__ == "__main__":
    main()
