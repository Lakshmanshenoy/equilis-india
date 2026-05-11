#!/bin/bash
# equity-report-to-pdf.sh
# Convert equity research markdown reports to beautiful PDFs
# Usage: ./equity-report-to-pdf.sh APCOTEXIND-Skill-Based-Report

set -e

REPORT_NAME="${1:?Error: Please provide report name (without extension)}"
MARKDOWN_FILE="${REPORT_NAME}.md"
HTML_FILE="/tmp/${REPORT_NAME}.html"
PDF_FILE="${REPORT_NAME}.pdf"
DOWNLOADS_DIR="${HOME}/Downloads"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}→${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Validate markdown file exists
if [ ! -f "$MARKDOWN_FILE" ]; then
    print_error "File not found: $MARKDOWN_FILE"
    echo "Please ensure the markdown report is in the current directory."
    exit 1
fi

print_status "Converting $MARKDOWN_FILE → HTML..."

# Create CSS styling inline (embedded in HTML)
STYLE_CSS="
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #2c3e50;
  margin: 0;
  padding: 20px;
  background: white;
  max-width: 900px;
  margin: 0 auto;
}

h1 {
  color: #1a5f7a;
  border-bottom: 3px solid #1a5f7a;
  padding-bottom: 10px;
  margin-top: 30px;
  font-size: 28px;
  font-weight: 700;
  page-break-after: avoid;
}

h2 {
  color: #2c5aa0;
  margin-top: 25px;
  font-size: 20px;
  font-weight: 600;
  page-break-after: avoid;
}

h3 {
  color: #34495e;
  margin-top: 18px;
  font-size: 16px;
  font-weight: 600;
  page-break-after: avoid;
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
  color: #d63384;
}

blockquote {
  border-left: 4px solid #1a5f7a;
  margin: 15px 0;
  padding: 10px 15px;
  background: #ecf7fb;
  color: #2c3e50;
  page-break-inside: avoid;
}

ul, ol {
  margin: 15px 0;
  padding-left: 25px;
}

li {
  margin: 8px 0;
}

a {
  color: #2c5aa0;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

@media print {
  body { background: white; padding: 0; }
  h1, h2, h3 { page-break-after: avoid; }
  table { page-break-inside: avoid; }
  tr { page-break-inside: avoid; }
  a { color: inherit; text-decoration: none; }
}
"

# Convert markdown to HTML using pandoc
if ! command -v pandoc &> /dev/null; then
    print_error "pandoc not found. Install with: brew install pandoc"
    exit 1
fi

pandoc -f markdown -t html "$MARKDOWN_FILE" \
    -o "$HTML_FILE" \
    --self-contained-html \
    --css <(echo "$STYLE_CSS") 2>/dev/null || true

# If pandoc CSS didn't work, try with string
if [ ! -f "$HTML_FILE" ]; then
    pandoc -f markdown -t html "$MARKDOWN_FILE" \
        -o "$HTML_FILE" \
        --self-contained-html
    
    # Add CSS to HTML file
    sed -i '' "s|</head>|<style>$STYLE_CSS</style></head>|" "$HTML_FILE"
fi

if [ ! -f "$HTML_FILE" ]; then
    print_error "HTML conversion failed"
    exit 1
fi

print_success "HTML generated"
print_status "Converting HTML → PDF (using Chrome)..."

# Check if Chrome is available
if [ ! -d "/Applications/Google Chrome.app" ]; then
    print_error "Google Chrome not found in /Applications"
    echo "Please install Google Chrome or use an alternative method."
    exit 1
fi

# Generate PDF using Chrome headless
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --headless \
    --disable-gpu \
    --print-to-pdf="${DOWNLOADS_DIR}/${PDF_FILE}" \
    "file://${HTML_FILE}" 2>/dev/null

# Verify PDF was created
if [ -f "${DOWNLOADS_DIR}/${PDF_FILE}" ]; then
    SIZE=$(ls -lh "${DOWNLOADS_DIR}/${PDF_FILE}" | awk '{print $5}')
    print_success "PDF generated successfully"
    echo ""
    echo "📄 Report: ${PDF_FILE}"
    echo "📍 Location: ${DOWNLOADS_DIR}/${PDF_FILE}"
    echo "💾 Size: ${SIZE}"
    echo ""
    print_status "Opening PDF..."
    open "${DOWNLOADS_DIR}/${PDF_FILE}"
else
    print_error "PDF generation failed"
    exit 1
fi

# Cleanup
rm -f "$HTML_FILE"

print_success "All done! 🎉"
