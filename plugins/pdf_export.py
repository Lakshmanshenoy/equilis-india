"""
plugins/pdf_export.py
PDF export plugin — renders analysis output to PDF.
Uses fpdf2 as primary renderer; falls back to weasyprint (HTML→PDF).
"""

import logging
import os
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.expanduser("~/Downloads/equilis-reports")


class PdfExportPlugin:
    """
    Generates PDF reports from analysis markdown or structured dicts.
    Not a BasePlugin subclass (doesn't fetch data — only renders).
    """

    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def render_markdown_to_pdf(self, markdown_text: str, ticker: str) -> str:
        """
        Convert a markdown string to a PDF file.
        Returns absolute path to the generated file.
        """
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{ticker.upper()}_{date_str}.pdf"
        out_path = os.path.join(self.output_dir, filename)

        try:
            self._render_weasyprint(markdown_text, out_path)
            logger.info(f"[pdf_export] Report saved to {out_path}")
            return out_path
        except Exception as e:
            logger.warning(f"[pdf_export] weasyprint failed ({e}), trying fpdf2")
            self._render_fpdf(markdown_text, out_path)
            return out_path

    def _render_weasyprint(self, markdown_text: str, out_path: str) -> None:
        from weasyprint import HTML
        import markdown as md_lib
        html_body = md_lib.markdown(markdown_text, extensions=["tables", "fenced_code"])
        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; margin: 40px; font-size: 11pt; }}
  h1, h2, h3 {{ color: #1a1a2e; }}
  table {{ border-collapse: collapse; width: 100%; margin-bottom: 1em; }}
  th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; }}
  th {{ background: #f0f0f0; }}
  blockquote {{ border-left: 4px solid #ccc; margin-left: 0; padding-left: 1em; color: #555; }}
  code {{ background: #f5f5f5; padding: 1px 4px; border-radius: 3px; }}
  .footer {{ font-size: 9pt; color: #888; border-top: 1px solid #ccc; margin-top: 2em; padding-top: 0.5em; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""
        HTML(string=html).write_pdf(out_path)

    def _render_fpdf(self, markdown_text: str, out_path: str) -> None:
        """Minimal plain-text fallback using fpdf2."""
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Helvetica", size=10)
        for line in markdown_text.split("\n"):
            # Strip markdown markers for plain-text rendering
            clean = line.lstrip("#").strip()
            if line.startswith("# "):
                pdf.set_font("Helvetica", style="B", size=14)
                pdf.cell(0, 8, clean, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", size=10)
            elif line.startswith("## "):
                pdf.set_font("Helvetica", style="B", size=12)
                pdf.cell(0, 7, clean, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", size=10)
            elif line.startswith("### "):
                pdf.set_font("Helvetica", style="B", size=11)
                pdf.cell(0, 6, clean, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", size=10)
            elif line.strip() == "---":
                pdf.ln(3)
                pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
                pdf.ln(3)
            else:
                pdf.multi_cell(0, 5, clean)
        pdf.output(out_path)
