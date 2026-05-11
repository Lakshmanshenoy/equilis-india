#!/usr/bin/env python3
"""
Equity Research Report to Beautiful PDF Converter
Converts markdown equity reports to professional-grade PDFs stored in ~/Downloads
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Optional

class ReportPDFGenerator:
    """Generate beautiful PDFs from equity research markdown reports"""
    
    def __init__(self, report_name: str, downloads_dir: str = "~/Downloads"):
        self.report_name = report_name
        self.markdown_file = Path(f"{report_name}.md")
        self.html_file = Path(f"/tmp/{report_name}.html")
        self.downloads_dir = Path(downloads_dir).expanduser()
        self.pdf_file = self.downloads_dir / f"{report_name}.pdf"
        
        # Professional CSS styling
        self.css_style = """
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
        """
    
    def print_status(self, message: str, symbol: str = "→"):
        """Print colored status message"""
        print(f"\033[0;34m{symbol}\033[0m {message}")
    
    def print_success(self, message: str):
        """Print colored success message"""
        print(f"\033[0;32m✓\033[0m {message}")
    
    def print_error(self, message: str):
        """Print colored error message"""
        print(f"\033[0;31m✗\033[0m {message}")
    
    def validate_inputs(self) -> bool:
        """Validate that markdown file exists"""
        if not self.markdown_file.exists():
            self.print_error(f"File not found: {self.markdown_file}")
            return False
        
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        return True
    
    def check_dependencies(self) -> bool:
        """Check if required tools are available"""
        # Check for pandoc
        try:
            subprocess.run(["pandoc", "--version"], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.print_error("pandoc not found. Install with: brew install pandoc")
            return False
        
        return True
    
    def markdown_to_html(self) -> bool:
        """Convert markdown to HTML"""
        self.print_status(f"Converting {self.markdown_file} → HTML...")
        
        try:
            subprocess.run([
                "pandoc",
                "-f", "markdown",
                "-t", "html",
                str(self.markdown_file),
                "-o", str(self.html_file),
                "--self-contained-html"
            ], check=True, capture_output=True)
            
            # Inject CSS styling
            with open(self.html_file, 'r') as f:
                html_content = f.read()
            
            # Insert CSS into head
            html_content = html_content.replace(
                '</head>',
                f'<style>{self.css_style}</style></head>'
            )
            
            with open(self.html_file, 'w') as f:
                f.write(html_content)
            
            self.print_success("HTML generated")
            return True
            
        except subprocess.CalledProcessError as e:
            self.print_error(f"HTML conversion failed: {e}")
            return False
    
    def html_to_pdf(self) -> bool:
        """Convert HTML to PDF using Chrome headless"""
        self.print_status("Converting HTML → PDF (using Chrome headless)...")
        
        chrome_path = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        
        if not chrome_path.exists():
            self.print_error("Google Chrome not found")
            self.print_status("Please install Google Chrome or use alternative method")
            return False
        
        try:
            subprocess.run([
                str(chrome_path),
                "--headless",
                "--disable-gpu",
                f"--print-to-pdf={self.pdf_file}",
                f"file://{self.html_file.absolute()}"
            ], check=True, capture_output=True, timeout=30)
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.print_error(f"PDF conversion failed: {e}")
            return False
        except subprocess.TimeoutExpired:
            self.print_error("PDF generation timed out")
            return False
    
    def cleanup(self):
        """Remove temporary HTML file"""
        if self.html_file.exists():
            self.html_file.unlink()
    
    def open_pdf(self):
        """Open the generated PDF"""
        try:
            subprocess.run(["open", str(self.pdf_file)], check=True)
        except subprocess.CalledProcessError:
            self.print_status(f"Open the PDF manually: {self.pdf_file}")
    
    def get_file_size(self) -> str:
        """Get human-readable file size"""
        size_bytes = self.pdf_file.stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def generate(self) -> bool:
        """Generate PDF from markdown report"""
        # Validate
        if not self.validate_inputs():
            return False
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Convert markdown → HTML
        if not self.markdown_to_html():
            return False
        
        # Convert HTML → PDF
        if not self.html_to_pdf():
            self.cleanup()
            return False
        
        # Cleanup
        self.cleanup()
        
        # Report success
        self.print_success("PDF generated successfully")
        print()
        print(f"📄 Report: {self.report_name}.pdf")
        print(f"📍 Location: {self.pdf_file}")
        print(f"💾 Size: {self.get_file_size()}")
        print()
        
        self.print_status("Opening PDF...")
        self.open_pdf()
        
        self.print_success("All done! 🎉")
        return True


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python3 equity-report-to-pdf.py <report-name>")
        print("Example: python3 equity-report-to-pdf.py APCOTEXIND-Skill-Based-Report")
        sys.exit(1)
    
    report_name = sys.argv[1]
    
    generator = ReportPDFGenerator(report_name)
    success = generator.generate()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
