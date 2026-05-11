# Equity Research PDF Generator

Quick reference guide for converting equity research reports to beautiful, professionally styled PDFs.

## 🚀 Quick Start (MAIN METHOD)

### Using Styled PDF Generator (RECOMMENDED - Always Use This)
```bash
~/equilis-india/skills/equity-research/tools/generate-styled-report-pdf.sh \
  /path/to/report.md \
  ~/Downloads/MyCompany-Research-Report.pdf
```

**Example:**
```bash
~/equilis-india/skills/equity-research/tools/generate-styled-report-pdf.sh \
  ~/Downloads/SONACOMS-Fresh-Equity-Research.md \
  ~/Downloads/SONACOMS-Equity-Research-2026-05-10.pdf
```

✅ **This method applies ALL professional styling automatically:**
- Blue gradient headers (#1a5f7a → #2c5aa0)
- Color-coded sections (Risk=Red, Valuation=Green, Financial=Blue)
- Professional typography with proper hierarchy
- Styled tables with alternating rows
- Automatic page breaks at logical points
- Print-ready formatting with 40px margins

### Alternative: Older Scripts (Legacy)
```bash
# Bash script (older method)
cd ~/Downloads
~/equilis-india/skills/equity-research/tools/equity-report-to-pdf.sh report-name

# Python script (older method)
python3 ~/equilis-india/skills/equity-research/tools/equity-report-to-pdf.py report-name
```

**⚠️ NOTE**: The new `generate-styled-report-pdf.sh` is MUCH better. Use that instead.

## 📋 What You Get

✓ **Professional-grade PDF** with:
- Beautiful gradient headers (blue tones)
- Formatted tables with alternating row colors
- Proper typography and spacing
- Page breaks at logical points
- 800-1200 KB file size (typical)

✓ **Auto-saved to**: `~/Downloads/`

✓ **Auto-opened** in Preview

## 📝 Prerequisites

### Required
- Google Chrome (for PDF rendering via headless mode)
- `pandoc` (for markdown → HTML conversion)

### Installation (if needed)
```bash
# Install pandoc
brew install pandoc

# Google Chrome - download from https://www.google.com/chrome/
# Or: brew install --cask google-chrome
```

## 🎨 Styling Features (Built-In)

The `generate-styled-report-pdf.sh` script automatically applies professional styling:

| Feature | Details |
|---------|---------|
| **Headers** | Blue gradients (#1a5f7a → #2c5aa0) with shadow effects |
| **Section Types** | Auto-colored: Risk (red), Valuation (green), Financial (blue) |
| **Tables** | Gradient headers, alternating row colors, professional spacing |
| **Typography** | Professional sans-serif, proper h1-h6 hierarchy, justified text |
| **Page Breaks** | Intelligent breaks after major sections, avoid splitting tables |
| **Margins** | 40px on all sides (A4 standard) |
| **Print Ready** | Color backgrounds enabled, optimized for PDF output |

### No Action Needed
All styling is **embedded in the script**. Just run it and the PDF comes out beautiful. ✨

## 🔧 Customization

### Modify Report Title/Formatting
Edit the markdown file before conversion. The script uses standard markdown formatting.

### Change Color Scheme
Edit the CSS in the script files:
- Bash: Look for `STYLE_CSS` variable
- Python: Look for `self.css_style` variable

### Change Output Location
```bash
# For bash script, modify DOWNLOADS_DIR
DOWNLOADS_DIR="/path/to/your/directory"

# For Python, pass downloads_dir parameter
python3 equity-report-to-pdf.py <name> --downloads "/path/to/your/directory"
```

## 📊 Markdown Best Practices for PDFs

### Optimal Heading Structure
```markdown
# Main Report Title (H1)

## Executive Summary (H2)
Brief overview...

### Key Findings (H3)
- Bullet point 1
- Bullet point 2

## Financial Analysis (H2)
Table content...
```

### Table Formatting
```markdown
| Metric | FY25 | FY26E | Change |
|--------|------|-------|--------|
| Revenue | ₹1,200 | ₹1,320 | +10% |
| EBITDA | ₹240 | ₹270 | +12.5% |
```

### Important Callouts
```markdown
> **Key Finding**: This is an important insight that 
> should stand out in the PDF with a blue left border.
```

### Proper Spacing
- Single blank line between sections
- Blank line before/after tables
- No excessive blank lines (confuses layout)

## ⚙️ Advanced Usage

### Batch Convert Multiple Reports
```bash
#!/bin/bash
for report in APCOTEX BRITANNIA RELIANCE; do
  ./equity-report-to-pdf.sh "$report-Report"
done
```

### Generate with Custom Name
Reports are generated with their markdown filename. To customize:
1. Rename markdown file: `mv old-name.md new-name.md`
2. Run script: `./equity-report-to-pdf.sh new-name`

### Monitor Progress
The script shows:
- ✓ HTML generation complete
- ✓ PDF generation complete
- ✓ File location and size

## 🐛 Troubleshooting

### "Chrome not found"
Install from: https://www.google.com/chrome/

### "Pandoc not found"
```bash
brew install pandoc
```

### "HTML conversion failed"
- Verify markdown file exists in current directory
- Check file encoding (should be UTF-8)
- Look for markdown syntax errors

### PDF looks weird / spacing issues
- Check for excessive blank lines in markdown
- Verify table column counts are consistent
- Ensure proper markdown link syntax: `[text](url)`

### File too large (> 2 MB)
- Remove or compress images
- Split into multiple reports
- Report is still readable at larger sizes

## 📈 Example Output

After running the script:
```
→ Converting APCOTEXIND-Skill-Based-Report.md → HTML...
✓ HTML generated
→ Converting HTML → PDF (using Chrome)...
✓ PDF generated successfully

📄 Report: APCOTEXIND-Skill-Based-Report.pdf
📍 Location: /Users/lakshmanshenoy/Downloads/APCOTEXIND-Skill-Based-Report.pdf
💾 Size: 800 KB

→ Opening PDF...
✓ All done! 🎉
```
