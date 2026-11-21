"""Draw the account's real contribution calendar and derived activity stats."""
import datetime as dt
from html import escape
import json

from svg_utils import DIM, FG, GREEN, ROOT, chrome, document

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def main() -> None:
    data = json.loads((ROOT / "data/contributions.json").read_text())
    days = data["days"]
    first = dt.date.fromisoformat(days[0]["date"])
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)
    end = dt.date.fromisoformat(days[-1]["date"])
    columns = ((end - start).days // 7) + 1
    step = min(14, 742 / max(columns, 1))
    size = step - 3
    x0, y0 = 57, 75
    body = chrome(860, "contributions.sh")
    months = set()
    for day in days:
        date = dt.date.fromisoformat(day["date"])
        column, row = divmod((date - start).days, 7)
        month = date.strftime("%Y-%m")
        if month not in months:
            months.add(month)
            body += f'<text x="{x0 + column * step:.1f}" y="62" fill="{DIM}" font-size="10">{date.strftime("%b")}</text>'
        x, y = x0 + column * step, y0 + row * 14
        delay = column * .018 + row * .028
        body += f'''<g class="cell" style="animation-delay:{delay:.3f}s">
<rect x="{x:.1f}" y="{y}" width="{size:.1f}" height="11" rx="2.2" fill="{PALETTE[day['level']]}"/>
<title>{day['date']}: {day['count']:,} contributions</title></g>'''
    for row, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        body += f'<text x="20" y="{y0 + row * 14 + 9}" fill="{DIM}" font-size="10">{label}</text>'
    total = data["total_contributions"]
    body += f'<text x="20" y="199" fill="{FG}" font-size="12"><tspan fill="{GREEN}" font-weight="700">{total:,}</tspan> contributions in the last year</text>'
    body += f'<text x="696" y="199" fill="{DIM}" font-size="10">Less</text>'
    for i, color in enumerate(PALETTE):
        body += f'<rect x="{729 + 14 * i}" y="190" width="10" height="10" rx="2" fill="{color}"/>'
    body += f'<text x="804" y="199" fill="{DIM}" font-size="10">More</text>'
    body += '<path d="M20 216H840" stroke="#21262d"/>'
    stats = [("CURRENT STREAK", f'{data["current_streak"]:,}', "days"),
             ("LONGEST STREAK", f'{data["longest_streak"]:,}', "days"),
             ("ACTIVE DAYS", f'{data["active_days"]:,}', "days"),
             ("BEST DAY", f'{data["best_day"]["count"]:,}', "contributions")]
    for i, (label, value, unit) in enumerate(stats):
        x = 24 + i * 210
        body += f'''<g class="reveal" style="animation-delay:{1.25 + i * .09:.2f}s">
<text x="{x}" y="241" fill="{DIM}" font-size="9">{label}</text>
<text x="{x}" y="271" fill="{FG}" font-size="25" font-weight="700">{value}<tspan fill="{DIM}" font-size="10"> {unit}</tspan></text></g>'''
    body += f'<text x="840" y="299" text-anchor="end" fill="{DIM}" font-size="9">public profile data · {escape(data["as_of"])} UTC · refreshed daily</text>'
    css = '''@keyframes cell-in { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }
.cell { animation: cell-in .28s ease-out both; }'''
    title = f'{data["username"]}: {total:,} contributions in the last year, {data["current_streak"]} day current streak'
    (ROOT / "contrib-heatmap.svg").write_text(document(860, 313, title, body, css))
    print(f"Wrote contrib-heatmap.svg ({columns} weeks)")


if __name__ == "__main__":
    main()
