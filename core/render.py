"""
core/render.py
Converts a research report markdown file to PDF.
Usage: python core/render.py --input reports/RELIANCE_20250501.md --output reports/RELIANCE_20250501.pdf
Requires: pip install weasyprint markdown
"""

import argparse
import os


def markdown_to_html(md_text: str) -> str:
    try:
        import markdown
        body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    except ImportError:
        raise ImportError("Install markdown: pip install markdown")

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Georgia, serif; font-size: 12pt; line-height: 1.6;
         margin: 2cm 2.5cm; color: #1a1a1a; }}
  h1 {{ font-size: 18pt; border-bottom: 2px solid #333; padding-bottom: 6px; }}
  h2 {{ font-size: 14pt; margin-top: 1.5em; }}
  h3 {{ font-size: 12pt; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 10pt; }}
  th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; }}
  th {{ background: #f2f2f2; font-weight: bold; }}
  code {{ font-family: monospace; background: #f5f5f5; padding: 2px 4px; font-size: 10pt; }}
  pre {{ background: #f5f5f5; padding: 12px; overflow-x: auto; font-size: 10pt; }}
  blockquote {{ border-left: 3px solid #999; margin-left: 0; padding-left: 1em; color: #555; }}
  .disclaimer {{ border: 1px solid #999; padding: 12px; font-size: 9pt;
                 background: #fafafa; margin-top: 2em; }}
</style>
</head>
<body>{body}</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Render markdown report to PDF.")
    parser.add_argument("--input", required=True, help="Input .md file path")
    parser.add_argument("--output", default=None, help="Output .pdf file path")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        md_text = f.read()

    html = markdown_to_html(md_text)
    output_path = args.output or args.input.replace(".md", ".pdf")

    try:
        from weasyprint import HTML
        HTML(string=html).write_pdf(output_path)
        print(f"PDF saved: {output_path}")
    except ImportError:
        raise ImportError("Install weasyprint: pip install weasyprint")


if __name__ == "__main__":
    main()
