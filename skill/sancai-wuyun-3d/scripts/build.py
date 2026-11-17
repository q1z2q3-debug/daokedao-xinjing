#!/usr/bin/env python3
"""把模板与 vendor 库拼成单文件三维模型 HTML。

用法：
    python3 scripts/build.py --list
    python3 scripts/build.py cup  --out 五蕴杯器-3D.html
    python3 scripts/build.py pipe --out 五蕴管壁-壁厚可调.html
    python3 scripts/build.py --template assets/templates/cup.html --out out.html

模板里必须各有一处 `/*__THREE__*/` 与 `/*__ORBIT__*/`，构建时被替换为
vendor/ 下的 three.js（r128）与 OrbitControls 源码。产物零外链、离线可开。
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "assets" / "templates"
VENDOR = ROOT / "vendor"
MODELS = {"cup": "cup.html", "pipe": "pipe.html"}


def inline(tpl_path: Path) -> str:
    src = tpl_path.read_text(encoding="utf-8")
    for mark, lib in (("/*__THREE__*/", "three.min.js"), ("/*__ORBIT__*/", "OrbitControls.js")):
        if mark not in src:
            sys.exit(f"模板缺少占位 {mark}：{tpl_path}")
        src = src.replace(mark, (VENDOR / lib).read_text(encoding="utf-8"), 1)
    return src


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("model", nargs="?", choices=list(MODELS), help="cup 或 pipe")
    ap.add_argument("--template", help="直接指定模板路径，替代 model")
    ap.add_argument("--out", required=False, help="产物路径")
    ap.add_argument("--list", action="store_true", help="列出可用模板")
    a = ap.parse_args()

    if a.list:
        for name, fn in MODELS.items():
            print(f"{name}\t{TPL / fn}")
        return

    tpl = Path(a.template) if a.template else TPL / MODELS[a.model]
    if not tpl.exists():
        sys.exit(f"模板不存在：{tpl}")
    out = Path(a.out or tpl.stem + "-built.html")
    out.write_text(inline(tpl), encoding="utf-8")
    print(f"{out}  {out.stat().st_size} bytes")


if __name__ == "__main__":
    main()
