#!/usr/bin/env python3
"""从 ../book/润泽说-道可道之心经通释（稿）.html 生成 APK 用的 assets。

做两件事：
  1. 把正文字体换成本地 @font-face（XinSerif），实现完全离线；
  2. 用系统 Noto Serif CJK SC 子集化出只含本书用字的 woff（400 / 700）。

产物不入库（体积大、可由本脚本重建）：
  apk/assets/book.html
  apk/assets/fonts/XinSerif-Regular.woff
  apk/assets/fonts/XinSerif-Bold.woff

用法：python3 prepare-assets.py
"""
import html, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "book", "心经通释·阅读版.html")
ASSETS = os.path.join(HERE, "assets")
FONTS = os.path.join(ASSETS, "fonts")

NOTO = {
    "Regular": ("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc", 2),
    "Bold":    ("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", 2),
}

FACE = """<style>
@font-face{font-family:"XinSerif";src:url("fonts/XinSerif-Regular.woff") format("woff");font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:"XinSerif";src:url("fonts/XinSerif-Bold.woff") format("woff");font-weight:600 900;font-style:normal;font-display:swap}
</style>"""

OLD = '"Noto Serif SC","Songti SC","Source Han Serif SC",serif;'
NEW = '"XinSerif","Noto Serif SC","Songti SC","Source Han Serif SC",serif;'


def build_html():
    s = open(SRC, encoding="utf-8").read()
    assert s.count(OLD) == 1, "正文字体声明结构变了，请检查阅读版 HTML"
    s = s.replace(OLD, NEW)
    assert "</head>" in s
    s = s.replace("</head>", FACE + "</head>", 1)
    os.makedirs(ASSETS, exist_ok=True)
    dst = os.path.join(ASSETS, "book.html")
    open(dst, "w", encoding="utf-8").write(s)
    print("book.html  %d 字节  外链 %d 处" % (os.path.getsize(dst), s.count("https://")))
    return s


def char_set(doc):
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", doc)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = html.unescape(t)
    base = {c for c in t if not c.isspace()}
    base |= {chr(i) for i in range(32, 127)}
    base |= set("　·—「」『』《》〈〉、。，；：？！…（）〔〕“”‘’　├│─")
    return base


def subset(chars):
    os.makedirs(FONTS, exist_ok=True)
    uni = ",".join("U+%04X" % ord(c) for c in sorted(chars) if ord(c) <= 0x10FFFF)
    for name, (path, idx) in NOTO.items():
        out = os.path.join(FONTS, "XinSerif-%s.woff" % name)
        cmd = [sys.executable, "-m", "fontTools.subset", path,
               "--font-number=%d" % idx, "--unicodes=" + uni,
               "--flavor=woff", "--layout-features=*",
               "--drop-tables+=DSIG", "--no-hinting",
               "--output-file=" + out]
        subprocess.run(cmd, check=True)
        print("%-22s %8d 字节" % (os.path.basename(out), os.path.getsize(out)))


if __name__ == "__main__":
    doc = build_html()
    cs = char_set(doc)
    print("用字 %d 个" % len(cs))
    subset(cs)
