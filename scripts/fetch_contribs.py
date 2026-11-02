import json, re, sys, requests
from bs4 import BeautifulSoup

USER = sys.argv[1] if len(sys.argv) > 1 else "Muurrcc"
html = requests.get(f"https://github.com/users/{USER}/contributions", timeout=30).text
soup = BeautifulSoup(html, "html.parser")

tips = {t.get("for"): t.get_text() for t in soup.find_all("tool-tip")}
days = []
for td in soup.select("td.ContributionCalendar-day"):
    if not td.get("data-date"):
        continue
    m = re.match(r"(\d+|No) contribution", tips.get(td.get("id"), ""))
    count = int(m.group(1)) if m and m.group(1) != "No" else 0
    days.append({"date": td["data-date"], "level": int(td.get("data-level", 0)), "count": count})
days.sort(key=lambda d: d["date"])

best = max(days, key=lambda d: d["count"], default={"count": 0, "date": ""})
cur = longest = run = 0
for d in days:
    run = run + 1 if d["count"] else 0
    longest = max(longest, run)
for d in reversed(days):
    if d["count"]:
        cur += 1
    elif d is not days[-1]:
        break

json.dump({"user": USER, "days": days, "total": sum(d["count"] for d in days),
           "best": best, "longest_streak": longest, "current_streak": cur},
          open("data/contribs.json", "w"), indent=1)
print(len(days), "days,", sum(d["count"] for d in days), "contributions")
