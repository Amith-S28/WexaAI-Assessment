"""
Export HTML Benchmark Report to High-Fidelity Publication-Grade PDF
Uses Headless Chrome or Edge to render the complete self-contained HTML report with all 29 diagrams,
tables, KPIs, and architectural synthesis into an exhaustive PDF document.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

POSSIBLE_BROWSER_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    shutil.which("chrome") or "",
    shutil.which("google-chrome") or "",
    shutil.which("msedge") or "",
    shutil.which("edge") or "",
]

def find_browser():
    for p in POSSIBLE_BROWSER_PATHS:
        if p and os.path.exists(p):
            return p
    return None

def export_html_to_pdf(html_path: Path, output_pdf_path: Path) -> bool:
    browser = find_browser()
    if not browser:
        print("[ERROR] No suitable browser (Chrome or Edge) found for PDF export.")
        return False
    
    html_abs = html_path.resolve()
    pdf_abs = output_pdf_path.resolve()
    pdf_abs.parent.mkdir(parents=True, exist_ok=True)
    
    # Remove existing output if present
    if pdf_abs.exists():
        try:
            pdf_abs.unlink()
        except Exception:
            pass

    file_url = "file:///" + str(html_abs).replace("\\", "/")
    
    cmd = [
        browser,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--allow-file-access-from-files",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=10000",
        f"--print-to-pdf={str(pdf_abs)}",
        file_url
    ]
    
    print(f"[*] Invoking browser PDF engine: {browser}")
    print(f"[*] Rendering: {html_abs}")
    print(f"[*] Target PDF: {pdf_abs}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if pdf_abs.exists() and pdf_abs.stat().st_size > 0:
            size_mb = pdf_abs.stat().st_size / (1024 * 1024)
            print(f"[OK] Successfully exported PDF: {pdf_abs} ({size_mb:.2f} MB)")
            return True
        else:
            print(f"[ERROR] Browser returned {result.returncode} but PDF was not generated.")
            if result.stderr:
                print(f"Stderr: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Exception during PDF export: {e}")
        return False

def verify_pdf_contents(pdf_path: Path):
    if not pdf_path.exists():
        print(f"[ERROR] Verification failed: {pdf_path} does not exist.")
        return
    
    size = pdf_path.stat().st_size
    print(f"\n--- PDF Verification Report for: {pdf_path.name} ---")
    print(f"File Size: {size:,} bytes ({size / (1024*1024):.2f} MB)")
    
    # Quick structural check
    with open(pdf_path, "rb") as f:
        header = f.read(1024)
        if b"%PDF" in header:
            print("PDF Format: Valid PDF Header detected")
        else:
            print("PDF Format: WARNING - No %PDF magic bytes found in header")

def main():
    repo_root = Path(__file__).resolve().parent.parent
    html_file = repo_root / "index.html"
    
    if not html_file.exists():
        html_file = repo_root / "Final Report" / "index.html"
        
    if not html_file.exists():
        print(f"[ERROR] HTML report not found at {html_file}")
        sys.exit(1)
        
    outputs = [
        repo_root / "Final Report" / "Wexa_AI_Graph_Database_Empirical_Benchmark_Report.pdf",
        repo_root / "Wexa_AI_Graph_Database_Empirical_Benchmark_Report.pdf",
        repo_root / "Final Report" / "index.pdf",
        repo_root / "index.pdf"
    ]
    
    primary_pdf = outputs[0]
    success = export_html_to_pdf(html_file, primary_pdf)
    
    if success:
        for out in outputs[1:]:
            try:
                shutil.copy2(primary_pdf, out)
                print(f"[OK] Synced copy to: {out}")
            except Exception as e:
                print(f"[WARN] Failed to copy to {out}: {e}")
                
        verify_pdf_contents(primary_pdf)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
