#!/bin/bash

# ============================================================================
# EQUITY RESEARCH - STYLED PDF GENERATOR
# ============================================================================
# This script converts markdown equity research reports to beautifully styled PDFs
# with professional typography, color-coded sections, and print-ready formatting.
#
# USAGE:
#   ./generate-styled-report-pdf.sh <input-markdown> <output-pdf>
#
# EXAMPLE:
#   ./generate-styled-report-pdf.sh SONACOMS-Research.md ~/Downloads/SONACOMS-Report-2026-05-10.pdf
#
# ============================================================================

set -e

INPUT_MD="${1:?Error: Please provide input markdown file}"
OUTPUT_PDF="${2:?Error: Please provide output PDF path}"

if [ ! -f "$INPUT_MD" ]; then
    echo "❌ Error: Input file '$INPUT_MD' not found"
    exit 1
fi

echo "🎨 Generating professionally styled PDF..."
echo "   Input:  $INPUT_MD"
echo "   Output: $OUTPUT_PDF"

# Step 1: Convert markdown to HTML
echo "   ⏳ Converting markdown to HTML..."
pandoc "$INPUT_MD" -t html -o /tmp/report_content.html 2>/dev/null || {
    echo "❌ Error: pandoc not found. Install with: brew install pandoc"
    exit 1
}

# Step 2: Create styled HTML wrapper with embedded CSS
echo "   ⏳ Applying professional styling..."
cat > /tmp/styled_report.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Equity Research Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        html, body {
            width: 100%;
            height: 100%;
        }
        
        body {
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.7;
            color: #2c3e50;
            background: white;
            padding: 40px;
            font-size: 11pt;
        }
        
        /* PAGE BREAKS */
        h1 {
            page-break-before: always;
            margin-top: 40px;
        }
        
        h1:first-of-type {
            page-break-before: avoid;
        }
        
        h2 {
            page-break-after: avoid;
            page-break-inside: avoid;
        }
        
        table {
            page-break-inside: avoid;
        }
        
        /* TYPOGRAPHY */
        h1 {
            background: linear-gradient(135deg, #1a5f7a 0%, #2c5aa0 100%);
            color: white;
            padding: 20px;
            margin: 40px 0 20px 0;
            border-radius: 8px;
            font-size: 24pt;
            font-weight: 700;
            box-shadow: 0 4px 6px rgba(0,0,0,0.15);
        }
        
        h2 {
            background: linear-gradient(90deg, #2c5aa0 0%, #3d6fb8 100%);
            color: white;
            padding: 12px 16px;
            margin: 25px 0 12px 0;
            border-radius: 5px;
            font-size: 14pt;
            font-weight: 600;
        }
        
        h3 {
            color: #1a5f7a;
            padding: 10px 0;
            margin: 16px 0 8px 0;
            border-left: 4px solid #2c5aa0;
            padding-left: 12px;
            font-size: 12pt;
            font-weight: 600;
            page-break-after: avoid;
        }
        
        h4, h5, h6 {
            color: #2c5aa0;
            margin: 8px 0;
            font-size: 11pt;
            font-weight: 600;
            page-break-after: avoid;
        }
        
        p {
            margin: 8px 0;
            text-align: justify;
        }
        
        /* TABLES */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            font-size: 10pt;
        }
        
        table th {
            background: linear-gradient(135deg, #1a5f7a 0%, #2c5aa0 100%);
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: 600;
            border: 1px solid #0f4a5f;
        }
        
        table td {
            padding: 8px 10px;
            border: 1px solid #ddd;
        }
        
        table tr:nth-child(even) {
            background-color: #f0f4f8;
        }
        
        table tr:hover {
            background-color: #e3eef7;
        }
        
        /* LISTS */
        ul, ol {
            margin: 12px 0 12px 25px;
        }
        
        li {
            margin: 6px 0;
            line-height: 1.6;
        }
        
        /* CODE & EMPHASIS */
        code {
            background: #f5f7fa;
            color: #d63384;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 9.5pt;
        }
        
        pre {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 12px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 12px 0;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
            page-break-inside: avoid;
        }
        
        strong {
            color: #1a5f7a;
            font-weight: 700;
        }
        
        em {
            color: #2c5aa0;
            font-style: italic;
        }
        
        /* SPECIAL SECTIONS - COLOR CODED */
        .risk-section {
            border-left: 5px solid #e74c3c;
            background: #ffecec;
            padding: 12px 15px;
            margin: 12px 0;
            page-break-inside: avoid;
        }
        
        .valuation-section {
            border-left: 5px solid #27ae60;
            background: #e8f5e9;
            padding: 12px 15px;
            margin: 12px 0;
            page-break-inside: avoid;
        }
        
        .financial-section {
            border-left: 5px solid #2e86ff;
            background: #f0f6ff;
            padding: 12px 15px;
            margin: 12px 0;
            page-break-inside: avoid;
        }
        
        blockquote {
            border-left: 4px solid #2c5aa0;
            padding-left: 15px;
            margin-left: 0;
            color: #555;
            font-style: italic;
            margin: 12px 0;
        }
        
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #2c5aa0, transparent);
            margin: 25px 0;
        }
        
        /* PRINT STYLES */
        @media print {
            body {
                background: white;
                padding: 40px;
            }
            
            a {
                color: inherit;
                text-decoration: none;
            }
            
            h1, h2 {
                page-break-after: avoid;
            }
            
            h1 {
                page-break-before: always;
            }
            
            table, .risk-section, .valuation-section, .financial-section {
                page-break-inside: avoid;
            }
        }
    </style>
</head>
<body>
EOF

# Insert the HTML content
cat /tmp/report_content.html >> /tmp/styled_report.html

# Close HTML
echo "</body></html>" >> /tmp/styled_report.html

# Step 3: Convert to PDF with Chrome headless
echo "   ⏳ Generating PDF with Chrome..."
if ! command -v google-chrome &> /dev/null && ! command -v chromium &> /dev/null && ! [ -d "/Applications/Google Chrome.app" ]; then
    echo "❌ Error: Google Chrome not found. Install with: brew install --cask google-chrome"
    exit 1
fi

# Try macOS path first, then Linux paths
CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [ ! -f "$CHROME_PATH" ]; then
    CHROME_PATH=$(which google-chrome || which chromium || echo "")
    if [ -z "$CHROME_PATH" ]; then
        echo "❌ Error: Chrome/Chromium not found in PATH"
        exit 1
    fi
fi

"$CHROME_PATH" \
    --headless \
    --disable-gpu \
    --print-to-pdf="$OUTPUT_PDF" \
    --print-to-pdf-no-header \
    file:///tmp/styled_report.html 2>&1 | grep -v "Registration response\|allocator\|integration\|externally_managed" || true

# Step 4: Verify and cleanup
if [ -f "$OUTPUT_PDF" ]; then
    SIZE=$(ls -lh "$OUTPUT_PDF" | awk '{print $5}')
    echo ""
    echo "✅ Success! Professional PDF generated"
    echo "   File: $OUTPUT_PDF"
    echo "   Size: $SIZE"
    echo ""
    echo "   Styling applied:"
    echo "   ✓ Blue gradient headers (#1a5f7a → #2c5aa0)"
    echo "   ✓ Color-coded sections (Risk=Red, Valuation=Green, Financial=Blue)"
    echo "   ✓ Professional typography with hierarchy"
    echo "   ✓ Styled tables with alternating rows"
    echo "   ✓ Automatic page breaks at logical points"
    echo "   ✓ Print-optimized spacing and margins"
    echo ""
    
    # Auto-open on macOS
    if [ "$(uname)" = "Darwin" ]; then
        open "$OUTPUT_PDF"
        echo "   Opening in Preview..."
    fi
else
    echo "❌ Error: PDF generation failed"
    exit 1
fi

# Cleanup
rm -f /tmp/report_content.html /tmp/styled_report.html
