"""Small helpers shared by the self-contained SVG renderers."""
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT = "ui-monospace,SFMono-Regular,Consolas,'Liberation Mono',monospace"
BG = "#0d1117"
FG = "#c9d1d9"
DIM = "#8b949e"
GREEN = "#3fb950"


def profile() -> dict:
    return json.loads((ROOT / "profile.json").read_text())


def document(width: int, height: int, title: str, body: str, css: str = "") -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">
<title id="title">{escape(title)}</title>
<style>
text {{ font-family: {FONT}; }}
@keyframes appear {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
.reveal {{ animation: appear .4s ease-out both; }}
{css}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" fill="{BG}" stroke="#30363d"/>
{body}
</svg>
'''


def chrome(width: int, filename: str) -> str:
    return f'''<path d="M1 35.5H{width - 1}" stroke="#21262d"/>
<circle cx="17" cy="18" r="3.5" fill="#f85149"/>
<circle cx="31" cy="18" r="3.5" fill="#d29922"/>
<circle cx="45" cy="18" r="3.5" fill="#3fb950"/>
<text x="{width - 15}" y="22" text-anchor="end" fill="{DIM}" font-size="10">{escape(filename)}</text>'''
