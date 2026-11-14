#!/usr/bin/env python3
"""把《心经通释》存入 Zenodo，取一个可引用的 DOI。

用法：
  export ZENODO_TOKEN=$(~/.daokedao-vault/cred zenodo)
  python3 scripts/zenodo-deposit.py --dry-run
  python3 scripts/zenodo-deposit.py --publish   # DOI 立即生效，不可撤销
"""
import argparse, json, os, urllib.request
from pathlib import Path

BASE = "https://zenodo.org/api"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
ROOT = Path(__file__).resolve().parent.parent
VER = "1.0.0"

FILES = [
    ("book/润泽说-道可道之心经通释（稿）.md", "daokedao-xinjing-v1.0.0.md"),
    ("book/心经通释·阅读版.html", "daokedao-xinjing-reader-v1.0.0.html"),
    ("packages/apk-1.0.0-xinjing/道可道-心经通释-1.0.0.apk", "daokedao-xinjing-reader-v1.0.0.apk"),
]

META = {"metadata": {
    "title": "润泽说 道可道之心经通释（v1.0.0）",
    "upload_type": "publication",
    "publication_type": "book",
    "publication_date": "2026-11-14",
    "version": VER,
    "language": "zho",
    "license": "cc-by-nc-sa-4.0",
    "creators": [{"name": "润泽"}],
    "keywords": ["心经", "般若", "佛教", "中国哲学", "老庄", "易传", "禅修"],
    "description": (
        "<p>《般若波罗蜜多心经》二百六十字的完整通释。全书 71,207 字，三十六节："
        "总序、卷首语、卷首附说、图一至图三、分释篇一至十一、附录总说、"
        "附录A至O（M、N 留空）、附录一至六、跋、编辑札记。</p>"
        "<p>方法：以「佛说A—即非A—是名A」为标尺，字源溯源、古义勘正、逐句拆解、跨典互证；"
        "以易、道、佛三参为一框架，兼通老庄与易传。底层模型为「三才五蕴太极空杯」。</p>"
        "<p>附件：Markdown 母本、单文件 HTML 阅读版（含封面、扉页、目录、三图内嵌与编注）、"
        "安卓离线包（零权限、断网可用、字体内置）。</p>"
    ),
    "related_identifiers": [
        {"relation": "isSupplementTo",
         "identifier": "https://github.com/q1z2q3-debug/daokedao-xinjing",
         "resource_type": "software"},
        {"relation": "isAlternateIdentifier",
         "identifier": "https://q1z2q3-debug.github.io/daokedao-xinjing/",
         "resource_type": "other"},
    ],
    "notes": "许可 CC BY-NC-SA 4.0。引用请注明书名与版本号 v1.0.0。",
}}

def call(url, token, data=None, method="POST", raw=None):
    body = raw if raw is not None else (json.dumps(data).encode() if data is not None else None)
    req = urllib.request.Request(url, data=body, method=method, headers={
        "Authorization": f"Bearer {token}", "User-Agent": UA,
        "Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--publish", action="store_true")
    a = ap.parse_args()
    token = os.environ.get("ZENODO_TOKEN") or ""
    if not token:
        raise SystemExit("缺 ZENODO_TOKEN")

    dep = call(BASE + "/deposit/depositions", token, {})
    dep_id = dep["id"]
    bucket = dep["links"]["bucket"]
    print("draft", dep_id, dep["links"]["html"])

    call(BASE + f"/deposit/depositions/{dep_id}", token, META, method="PUT")

    for path, name in FILES:
        data = (ROOT / path).read_bytes()
        req = urllib.request.Request(f"{bucket}/{name}", data=data, method="PUT", headers={
            "Authorization": f"Bearer {token}", "User-Agent": UA,
            "Content-Type": "application/octet-stream"})
        with urllib.request.urlopen(req, timeout=600) as r:
            j = json.load(r)
        print("  up", j.get("key"), j.get("size"))

    if a.publish:
        pub = call(BASE + f"/deposit/depositions/{dep_id}/actions/publish", token, {}, method="POST")
        print("DOI", pub.get("doi"), pub.get("links", {}).get("doi"))
    else:
        print("草稿未发布：", dep["links"]["html"])

if __name__ == "__main__":
    main()
