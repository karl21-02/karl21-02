"""Print a monochrome portrait row-by-row, then keep the final frame."""
from html import escape

from PIL import Image, ImageOps

from svg_utils import DIM, ROOT, chrome, document, profile

RAMP = " .`:-=+*cs#%@"


def main() -> None:
    # Account for the approximately 1:2 aspect ratio of monospace glyphs.
    source = Image.open(ROOT / "assets/source-prepped.png").convert("L")
    canvas = Image.new("L", (192, 212), 255)
    fitted = ImageOps.contain(source, canvas.size, Image.Resampling.LANCZOS)
    canvas.paste(fitted, ((192 - fitted.width) // 2, (212 - fitted.height) // 2))
    pixels = canvas.resize((96, 53), Image.Resampling.LANCZOS)
    definitions, lines = [], []
    for row in range(53):
        y = 49 + row * 5.8
        delay = row * .035
        chars = "".join(RAMP[min(len(RAMP) - 1, int((255 - pixels.getpixel((col, row))) / 256 * len(RAMP)))]
                        for col in range(96))
        definitions.append(f'<clipPath id="row{row}"><rect class="wipe" x="20" y="{y - 5:.1f}" width="330" height="6" style="animation-delay:{delay:.3f}s"/></clipPath>')
        lines.append(f'<text x="20" y="{y:.1f}" fill="#b1bac4" font-size="5.65" letter-spacing="0" xml:space="preserve" clip-path="url(#row{row})">{escape(chars)}</text>')
    css = '''@keyframes type { from { width: 0; } to { width: 330px; } }
.wipe { animation: type .20s linear both; }'''
    body = chrome(370, "portrait.svg") + "<defs>" + "".join(definitions) + "</defs>" + "".join(lines)
    body += f'<text x="185" y="361" text-anchor="middle" fill="{DIM}" font-size="9">{escape(profile()["username"])}</text>'
    output = document(370, 374, f'{profile()["name"]} — monochrome ASCII portrait', body, css)
    (ROOT / "karl-ascii.svg").write_text(output)
    print("Wrote karl-ascii.svg")


if __name__ == "__main__":
    main()
