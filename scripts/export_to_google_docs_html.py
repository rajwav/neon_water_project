"""
Convert SIH Master Dossiers to Clean Styled HTML for Seamless Google Docs Copy-Pasting.
"""

import html
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"


def md_to_gdocs_html(md_path: Path, out_path: Path, doc_title: str) -> None:
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    html_lines = []
    in_table = False
    in_code = False

    for line in lines:
        raw = line.rstrip()
        stripped = raw.strip()

        if stripped.startswith("```"):
            if in_code:
                html_lines.append("</pre>")
                in_code = False
            else:
                html_lines.append(
                    '<pre style="background-color:#F8FAFC; border:1px solid #CBD5E1; padding:12px; border-radius:6px; font-family:Courier New, monospace; font-size:9.5pt; overflow-x:auto;">'
                )
                in_code = True
            continue

        if in_code:
            html_lines.append(html.escape(raw))
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if all(set(c).issubset({"-", ":", " "}) for c in cells):
                continue

            if not in_table:
                in_table = True
                html_lines.append(
                    '<table style="border-collapse:collapse; width:100%; margin:16px 0; font-size:10pt; border:1px solid #94A3B8;">'
                )
                html_lines.append('<thead><tr style="background-color:#E2E8F0;">')
                for c in cells:
                    formatted_h = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", c)
                    html_lines.append(
                        f'<th style="border:1px solid #94A3B8; padding:8px 10px; text-align:left; color:#0F172A; font-weight:bold;">{formatted_h}</th>'
                    )
                html_lines.append("</tr></thead><tbody>")
            else:
                html_lines.append('<tr style="border-bottom:1px solid #CBD5E1;">')
                for c in cells:
                    formatted = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", c)
                    formatted = re.sub(
                        r"`(.*?)`",
                        r'<code style="background-color:#F1F5F9; padding:2px 4px; border-radius:3px;">\1</code>',
                        formatted,
                    )
                    html_lines.append(
                        f'<td style="border:1px solid #94A3B8; padding:8px 10px; text-align:left; vertical-align:top;">{formatted}</td>'
                    )
                html_lines.append("</tr>")
            continue
        else:
            if in_table:
                html_lines.append("</tbody></table>")
                in_table = False

        if stripped.startswith("# "):
            html_lines.append(
                f'<h1 style="color:#1E3A8A; font-size:20pt; border-bottom:2px solid #1E3A8A; padding-bottom:6px; margin-top:24pt; font-family:Arial, sans-serif;">{stripped[2:]}</h1>'
            )
        elif stripped.startswith("## "):
            html_lines.append(
                f'<h2 style="color:#1E40AF; font-size:15pt; border-bottom:1px solid #CBD5E1; padding-bottom:4px; margin-top:18pt; font-family:Arial, sans-serif;">{stripped[3:]}</h2>'
            )
        elif stripped.startswith("### "):
            html_lines.append(
                f'<h3 style="color:#0F766E; font-size:12pt; margin-top:14pt; font-family:Arial, sans-serif;">{stripped[4:]}</h3>'
            )
        elif stripped.startswith("#### "):
            html_lines.append(
                f'<h4 style="color:#1F2937; font-size:11pt; font-weight:bold; margin-top:12pt; font-family:Arial, sans-serif;">{stripped[5:]}</h4>'
            )
        elif stripped.startswith("> "):
            html_lines.append(
                f'<div style="border-left:4px solid #3B82F6; background-color:#EFF6FF; padding:8px 14px; margin:10px 0; color:#1E40AF; border-radius:0 4px 4px 0;">{stripped[2:]}</div>'
            )
        elif stripped.startswith("- ") or stripped.startswith("* "):
            formatted = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", stripped[2:])
            formatted = re.sub(
                r"`(.*?)`",
                r'<code style="background-color:#F1F5F9; padding:2px 4px; border-radius:3px;">\1</code>',
                formatted,
            )
            html_lines.append(f'<li style="margin-bottom:4px; margin-left:20px; line-height:1.5;">{formatted}</li>')
        elif stripped == "---":
            html_lines.append('<hr style="border:none; border-top:1px solid #CBD5E1; margin:20px 0;">')
        elif stripped:
            formatted = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", stripped)
            formatted = re.sub(
                r"`(.*?)`",
                r'<code style="background-color:#F1F5F9; padding:2px 4px; border-radius:3px;">\1</code>',
                formatted,
            )
            html_lines.append(f'<p style="margin-bottom:8px; line-height:1.5;">{formatted}</p>')

    if in_table:
        html_lines.append("</tbody></table>")
    if in_code:
        html_lines.append("</pre>")

    doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{doc_title}</title>
<style>
body {{
    font-family: 'Arial', 'Calibri', sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #111827;
    max-width: 900px;
    margin: 30px auto;
    padding: 24px;
}}
</style>
</head>
<body>
{''.join(html_lines)}
</body>
</html>"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)


if __name__ == "__main__":
    dossier_md = DOCS_DIR / "SIH_TECHNICAL_DEFENSE_MASTER_DOSSIER.md"
    dossier_html = DOCS_DIR / "SIH_TECHNICAL_DEFENSE_FOR_GOOGLE_DOCS.html"
    md_to_gdocs_html(dossier_md, dossier_html, "AQUA NEON - Technical Defense Master Dossier")

    q100_md = DOCS_DIR / "SIH_100_HARD_JUDGE_QUESTIONS_MASTER_DEFENSE.md"
    q100_html = DOCS_DIR / "SIH_100_JUDGE_QUESTIONS_FOR_GOOGLE_DOCS.html"
    md_to_gdocs_html(q100_md, q100_html, "AQUA NEON - 100 Hard Judge Questions Master Defense")

    print(f"Generated: {dossier_html}")
    print(f"Generated: {q100_html}")
