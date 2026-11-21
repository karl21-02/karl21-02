"""Generate the neofetch-style introduction, with finite line reveals."""
from html import escape

from svg_utils import DIM, FG, GREEN, ROOT, chrome, document, profile


def main() -> None:
    p = profile()
    body = chrome(490, "whoami")
    body += f'<text x="25" y="69" fill="{GREEN}" font-size="19" font-weight="700">{escape(p["username"])}@github</text>'
    body += '<path d="M25 85H465" stroke="#30363d" stroke-dasharray="4 4"/>'
    rows = [
        ("Name", p["name"]),
        ("Bio", p["bio"]),
        ("Code", p["code"]),
        ("Build", p["build"]),
        ("Projects", " / ".join(item["name"] for item in p["projects"])),
        ("Web", p["portfolio"].replace("https://", "").rstrip("/")),
    ]
    for i, (label, value) in enumerate(rows):
        y = 116 + i * 32
        size = 11.5 if label in ("Projects", "Web") else 13
        body += f'''<g class="reveal" style="animation-delay:{.2 + i * .14:.2f}s">
<text x="25" y="{y}" fill="{GREEN}" font-size="12" font-weight="600">{label}</text>
<text x="104" y="{y}" fill="{FG}" font-size="{size}">{escape(value)}</text>
</g>'''
    for i, color in enumerate(["#30363d", "#f85149", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9"]):
        body += f'<rect x="{25 + i * 25}" y="320" width="25" height="13" fill="{color}"/>'
    body += f'<text x="25" y="356" fill="{DIM}" font-size="10">$ echo "{escape(p["bio"])}"</text>'
    (ROOT / "info-card.svg").write_text(document(490, 374, f'{p["name"]} — {p["build"]}', body))
    print("Wrote info-card.svg")


if __name__ == "__main__":
    main()
