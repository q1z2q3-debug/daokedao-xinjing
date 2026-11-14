#!/usr/bin/env python3
"""从阅读版 HTML 生成 A5 成书 PDF（封面、扉页整页 + 正文分页 + 页眉页码）。

用法：python3 scripts/build_pdf.py
产物：book/润泽说 道可道之心经通释.pdf
"""
import os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "book/心经通释·阅读版.html"
TMP = Path("/tmp/xinjing_print.html")
OUT = ROOT / "book/润泽说 道可道之心经通释.pdf"

PRINT_CSS = """
<style>
@page{size:148mm 210mm;margin:15mm 14mm 17mm;}
@media print{
  body{background:#fff;}
  .page{max-width:none;padding:0;margin:0;}
  .plate{max-width:none;margin:0;height:auto;display:block;page-break-after:always;}
  .plate img{width:100%;height:auto;box-shadow:none;}
  nav.toc{page-break-after:always;}
  h2{page-break-before:always;font-size:17pt;margin:0 0 12pt;padding-top:0;border-top:0;}
  h2:first-of-type{page-break-before:auto;}
  h3{font-size:11pt;margin:14pt 0 6pt;}
  p{font-size:10.2pt;line-height:1.75;margin:0 0 8pt;}
  li{font-size:10pt;line-height:1.7;}
  blockquote p,.ednote p{font-size:9.2pt;line-height:1.65;}
  figure img{max-width:100%;height:auto;}
  .foot{display:none;}
  .toc li a{font-size:10pt;}
}
</style>
"""

def main():
    s = SRC.read_text(encoding="utf-8")
    s = s.replace("</head>", PRINT_CSS + "</head>", 1)
    TMP.write_text(s, encoding="utf-8")

    code = r'''
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/opt/vm/preinstall/ms-playwright/chromium-1169/chrome-linux/chrome")
    pg=b.new_page()
    pg.goto("file://__TMP__", wait_until="networkidle")
    pg.wait_for_timeout(1200)
    pg.pdf(path="__OUT__", format="A5", print_background=True, prefer_css_page_size=True)
    b.close()
'''
    code = code.replace("__TMP__", str(TMP)).replace("__OUT__", str(OUT))
    subprocess.run([sys.executable, "-c", code], check=True)
    print("pdf", OUT.stat().st_size, "字节")

if __name__ == "__main__":
    main()
