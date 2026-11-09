#!/usr/bin/env python3
"""检查 Markdown 里的相对链接与图片引用是否都存在。

用法：
    python scripts/check_links.py .              # 全量检查
    python scripts/check_links.py docs/          # 只查某目录

退出码 0 表示全部通过，1 表示存在失效引用（可直接用于 CI）。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# 行内链接 [text](target)  与  图片 ![alt](target)
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
# 引用式定义 [id]: target
REF_RE = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
# 围栏代码块 ```lang ... ```
FENCE_RE = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)
# 行内代码 `code`
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def mask_code(text: str) -> str:
    """把代码块与行内代码替换为空白，避免把示例路径当成真实引用。

    保持字符数不变不重要，只要不参与匹配即可。
    """
    text = FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    text = INLINE_CODE_RE.sub("", text)
    return text


def strip_target(target: str) -> str:
    """去掉 title、锚点与包裹的尖括号，返回纯路径。"""
    target = target.strip()
    # [text](<path with space>) 形式
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    # [text](path "title")
    if " " in target and not target.startswith("http"):
        target = target.split(" ")[0]
    # 去掉 #anchor
    target = target.split("#")[0]
    return target


def is_external(target: str) -> bool:
    return bool(re.match(r"^(https?:|mailto:|tel:|ftp:)", target)) or target.startswith("//")


def check(root: Path) -> tuple[int, int, list[str]]:
    errors: list[str] = []
    files = sorted(p for p in root.rglob("*.md") if ".git" not in p.parts)
    checked = 0

    for md in files:
        raw_text = md.read_text(encoding="utf-8", errors="replace")
        text = mask_code(raw_text)
        targets = LINK_RE.findall(text) + REF_RE.findall(text)

        for raw in targets:
            target = strip_target(raw)
            if not target or is_external(target):
                continue
            checked += 1

            # 绝对路径 /xxx 在 GitHub 上是仓库根路径
            if target.startswith("/"):
                resolved = root / target.lstrip("/")
            else:
                resolved = (md.parent / target).resolve()

            if not resolved.exists():
                rel_md = md.relative_to(root)
                errors.append(f"{rel_md}  ->  {raw}")

    return checked, len(files), errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    if not root.exists():
        print(f"目录不存在：{root}", file=sys.stderr)
        return 1

    checked, file_count, errors = check(root)
    print(f"检查 {file_count} 个 Markdown 文件，{checked} 条相对引用\n")

    if errors:
        print(f"发现 {len(errors)} 条失效引用：\n")
        for e in errors:
            print(f"  ✗ {e}")
        print("\n修复方式：确认文件是否建立、路径层级是否正确（../ 的数量）。")
        return 1

    print("全部通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
