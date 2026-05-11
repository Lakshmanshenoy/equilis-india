# PDF Report Generation & Formatting

Professional PDF generation for equity research reports with beautiful layouts, styling, and output optimization.

## Quick Start

**Pre-built scripts ready to use:**
```bash
skills/equity-research/tools/equity-report-to-pdf.sh <report-name>
# or
python3 skills/equity-research/tools/equity-report-to-pdf.py <report-name>
```

**Example:**
```bash
cd ~/Downloads
skills/equity-research/tools/equity-report-to-pdf.sh APCOTEXIND-Skill-Based-Report
```

---

## Overview

Convert equity research markdown reports into publication-ready PDFs with professional formatting, tables, charts, and visual hierarchy. Supports multiple generation methods optimized for different environments.

All PDF outputs go to `~/Downloads` by default.

---

## Method 1: Chrome Headless (Recommended for macOS/Linux)

**Advantages**: Native OS support, excellent layout rendering, high-quality output
**File size**: ~800 KB for 20+ page reports
**Quality**: Professional-grade PDF

### Prerequisites
- Google Chrome or Chromium browser installed
- Report in HTML format (convert from markdown via pandoc)

### Conversion Pipeline

**Step 1: Markdown → HTML**
```bash
pandoc -f markdown -t html \
  APCOTEXIND-Skill-Based-Report.md \
  -o report.html \
  --css=style.css \
  --self-contained-html
```

**Step 2: HTML → PDF (Chrome Headless)**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless \
  --disable-gpu \
  --print-to-pdf=/path/to/Downloads/report.pdf \
  file:///path/to/report.html
```

### CSS Styling for Beautiful Output

Create `style.css` with professional formatting:

```css
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #2c3e50;
  margin: 0;
  padding: 20px;
  background: white;
}

h1 {
  color: #1a5f7a;
  border-bottom: 3px solid #1a5f7a;
  padding-bottom: 10px;
  margin-top: 30px;
  font-size: 28px;
  font-weight: 700;
}

h2 {
  color: #2c5aa0;
  margin-top: 25px;
  font-size: 20px;
  font-weight: 600;
}

h3 {
  color: #34495e;
  margin-top: 18px;
  font-size: 16px;
  font-weight: 600;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 15px 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  page-break-inside: avoid;
}

th {
  background: linear-gradient(135deg, #1a5f7a 0%, #2c5aa0 100%);
  color: white;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #0f3c4f;
}

td {
  padding: 10px 12px;
  border-bottom: 1px solid #ecf0f1;
}

tr:nth-child(even) {
  background-color: #f8f9fa;
}

tr:hover {
  background-color: #e8f4f8;
}

code {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

blockquote {
  border-left: 4px solid #1a5f7a;
  margin: 15px 0;
  padding: 10px 15px;
  background: #ecf7fb;
  color: #2c3e50;
}

ul, ol {
  margin: 15px 0;
  padding-left: 25px;
}

li {
  margin: 8px 0;
}

@media print {
  body { background: white; }
  h1, h2, h3 { page-break-after: avoid; }
  table { page-break-inside: avoid; }
  tr { page-break-inside: avoid; }
}
```

### Alias Setup

```bash
# Add to ~/.zshrc for easy access
alias equity-pdf="~/equilis-india/skills/equity-research/tools/equity-report-to-pdf.sh"
```

**Usage:**
```bash
cd ~/Downloads
equity-pdf APCOTEXIND-Skill-Based-Report
```

---

## Method 2: Styled Report (Recommended for Best Output)

The `generate-styled-report-pdf.sh` script produces the best visual quality with gradient headers, color-coded sections, and embedded CSS.

```bash
skills/equity-research/tools/generate-styled-report-pdf.sh \
  ~/Downloads/BLUEJET-Research.md \
  ~/Downloads/BLUEJET-Research.pdf
```

---

## Method 3: Python-based (WeasyPrint)

**Advantages**: Fully programmable, integrates with Python pipelines
**Requirements**: `pip install weasyprint Pillow`

```python
#!/usr/bin/env python3
"""Convert markdown equity report to beautiful PDF"""
# See tools/equity-report-to-pdf.py for the full implementation
```

---

## Output Standards

| Metric | Target |
|--------|--------|
| File size | ~800 KB for 20-page report |
| Format | A4, portrait |
| Output location | ~/Downloads (always) |
| File naming | `TICKER-Report-YYYY-MM-DD.pdf` |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Chrome not found | Install Google Chrome or update path in script |
| pandoc not found | `brew install pandoc` |
| HTML conversion failed | Check markdown syntax for unclosed code blocks |
| Large file size | Reduce image count; use --print-to-pdf-no-header flag |
| Weird formatting | Inspect HTML first; check CSS |
