"""Read the same public contribution calendar shown on the GitHub profile."""
import datetime as dt
import json
import os
from pathlib import Path
import re

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]


def validate_calendar(days: list[dict], today: dt.date) -> None:
    dates = sorted(dt.date.fromisoformat(day["date"]) for day in days)
    if not 365 <= len(dates) <= 371:
        raise ValueError("Incomplete yearly calendar; refusing to replace stored data")
    if dates[-1] < today - dt.timedelta(days=1) or dates[-1] > today:
        raise ValueError("Calendar is stale or contains future dates")
    if dates[0] > today - dt.timedelta(days=364):
        raise ValueError("Calendar does not cover the last year")
    if any(right - left != dt.timedelta(days=1) for left, right in zip(dates, dates[1:])):
        raise ValueError("Calendar has missing or duplicate dates")


def parse_contributions(html: str, today: dt.date) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    tooltips = {tip.get("for"): tip.get_text(" ", strip=True)
                for tip in soup.find_all("tool-tip")}
    days = {}
    for cell in soup.select("td.ContributionCalendar-day[data-date]"):
        date = dt.date.fromisoformat(cell["data-date"])
        if date > today:
            continue
        label = tooltips.get(cell.get("id"), "") or cell.get("aria-label", "")
        match = re.match(r"([\d,]+)\s+contributions?\b", label, re.I)
        if re.match(r"no contributions\b", label, re.I):
            count = 0
        elif match:
            count = int(match[1].replace(",", ""))
        else:
            raise ValueError(f"Cannot read contribution count for {date}: calendar markup changed")
        if "data-level" not in cell.attrs:
            raise ValueError(f"Missing contribution color level for {date}")
        level = int(cell["data-level"])
        if not 0 <= level <= 4:
            raise ValueError(f"Invalid contribution color level for {date}")
        key = date.isoformat()
        if key in days:
            raise ValueError(f"Duplicate contribution date: {key}")
        days[key] = {"date": key, "count": count, "level": level}
    if not days:
        raise ValueError("No contribution calendar found; refusing to replace stored data")
    return [days[key] for key in sorted(days)]


def build_data(days: list[dict], today: dt.date) -> dict:
    days = sorted((day for day in days if dt.date.fromisoformat(day["date"]) <= today),
                  key=lambda day: day["date"])
    if not days:
        raise ValueError("Contribution data is empty")
    counts = {dt.date.fromisoformat(day["date"]): day["count"] for day in days}
    end = today if counts.get(today, 0) else today - dt.timedelta(days=1)
    current = 0
    while counts.get(end, 0) > 0:
        current += 1
        end -= dt.timedelta(days=1)
    longest = run = 0
    previous = None
    monthly = {}
    for day in days:
        date = dt.date.fromisoformat(day["date"])
        if previous is not None and date != previous + dt.timedelta(days=1):
            run = 0
        run = run + 1 if day["count"] else 0
        longest = max(longest, run)
        previous = date
        month = day["date"][:7]
        monthly[month] = monthly.get(month, 0) + day["count"]
    return {
        "username": os.environ.get("GH_PROFILE_USER", "karl21-02"),
        "as_of": today.isoformat(),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": sum(day["count"] for day in days),
        "active_days": sum(day["count"] > 0 for day in days),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": max(days, key=lambda day: day["count"]),
        "monthly": monthly,
        "days": days,
    }


def main() -> None:
    username = os.environ.get("GH_PROFILE_USER", "karl21-02")
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", username):
        raise ValueError("Invalid GitHub username")
    response = requests.get(f"https://github.com/users/{username}/contributions",
                            headers={"User-Agent": "karl21-02-profile/1.0"}, timeout=30)
    response.raise_for_status()
    today = dt.datetime.now(dt.timezone.utc).date()
    days = parse_contributions(response.text, today)
    validate_calendar(days, today)
    data = build_data(days, today)
    output = ROOT / "data/contributions.json"
    output.parent.mkdir(exist_ok=True)
    temporary = output.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(output)
    print(f"{username}: {data['total_contributions']:,} contributions across {len(data['days'])} days")


if __name__ == "__main__":
    main()
