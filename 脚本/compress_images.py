#!/usr/bin/env python3
"""压缩仓库内的图片，并检查体积与命名规范。

BI 截图的文字是主体，转 JPG 会让文字边缘发毛，所以这里只做 PNG 量化压缩
（减少颜色数 + 优化调色板），视觉上无损，体积通常降到 1/3 左右。

用法：
    python scripts/compress_images.py docs/                 # 预演，只报告不修改
    python scripts/compress_images.py docs/ --apply         # 实际压缩并覆盖
    python scripts/compress_images.py . --check             # 只做规范检查

依赖：
    pip install pillow
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
# GitHub 单文件硬限制 100MB，超过直接拒绝推送
HARD_LIMIT = 100 * 1024 * 1024
# 单张图片超过这个尺寸基本是没压缩的原始截图
WARN_SIZE = 800 * 1024
# 整个仓库图片总量的建议上限
TOTAL_BUDGET = 100 * 1024 * 1024
# 命名规范：小写字母数字开头，只含小写字母、数字、连字符
NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9\-]*\.(png|jpg|jpeg|gif|webp)$")


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def collect(root: Path) -> list[Path]:
    return sorted(
        p
        for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS and ".git" not in p.parts
    )


def check_names(files: list[Path]) -> list[tuple[Path, str]]:
    """返回命名不合规的文件及原因。"""
    bad = []
    for p in files:
        if not NAME_PATTERN.match(p.name):
            reason = "含中文/空格/大写/无效字符"
            if re.search(r"[\u4e00-\u9fff]", p.name):
                reason = "文件名含中文"
            elif " " in p.name:
                reason = "文件名含空格"
            elif p.name != p.name.lower():
                reason = "文件名含大写字母"
            bad.append((p, reason))
    return bad


def check_placement(files: list[Path], root: Path) -> list[Path]:
    """图片应位于某目录的 images/ 下，或位于根 assets/ 下。"""
    misplaced = []
    for p in files:
        parts = p.relative_to(root).parts
        if "images" in parts or (parts and parts[0] == "assets"):
            continue
        misplaced.append(p)
    return misplaced


def compress_png(path: Path, apply: bool, colors: int) -> tuple[int, int]:
    """PNG 量化压缩。返回 (原大小, 新大小)。失败时返回相等值。"""
    try:
        from PIL import Image
    except ImportError:
        print("  缺少依赖：pip install pillow", file=sys.stderr)
        return path.stat().st_size, path.stat().st_size

    original = path.stat().st_size
    if path.suffix.lower() != ".png":
        return original, original

    tmp = path.with_suffix(".png.tmp")
    try:
        with Image.open(path) as im:
            # 截图多为 RGB/RGBA，量化前转成 RGB 会丢透明通道，所以保留模式
            has_alpha = im.mode in ("RGBA", "LA", "P")
            im = im.convert("RGBA" if has_alpha else "RGB")
            quant = im.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
            quant.save(tmp, format="PNG", optimize=True)
        new = tmp.stat().st_size
        if new < original and apply:
            tmp.replace(path)
            return original, new
        tmp.unlink(missing_ok=True)
        return original, new if new < original else original
    except Exception as exc:  # 单张失败不影响整体
        tmp.unlink(missing_ok=True)
        print(f"  跳过 {path.name}: {exc}", file=sys.stderr)
        return original, original


def main() -> int:
    ap = argparse.ArgumentParser(description="压缩图片并检查仓库规范")
    ap.add_argument("root", nargs="?", default=".", help="要处理的目录")
    ap.add_argument("--apply", action="store_true", help="实际写入压缩结果")
    ap.add_argument("--check", action="store_true", help="只做规范检查，不压缩")
    ap.add_argument("--colors", type=int, default=256, help="PNG 调色板颜色数，默认 256")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"目录不存在：{root}", file=sys.stderr)
        return 1

    files = collect(root)
    if not files:
        print(f"{root} 下没有找到图片。")
        return 0

    total_before = sum(p.stat().st_size for p in files)
    print(f"扫描到 {len(files)} 张图片，合计 {human(total_before)}\n")

    print("— 命名检查 —")
    bad_names = check_names(files)
    if bad_names:
        for p, reason in bad_names:
            print(f"  ✗ {p.relative_to(root)}  ({reason})")
        print(f"  共 {len(bad_names)} 个待改名：章节号-主题-序号.png\n")
    else:
        print("  全部符合规范\n")

    print("— 位置检查 —")
    misplaced = check_placement(files, root)
    if misplaced:
        for p in misplaced:
            print(f"  ✗ {p.relative_to(root)}")
        print("  以上图片不在 images/ 或 assets/ 下，建议移动\n")
    else:
        print("  全部位置正确\n")

    print("— 体积检查 —")
    oversize = [(p, p.stat().st_size) for p in files if p.stat().st_size > WARN_SIZE]
    for p, size in sorted(oversize, key=lambda x: -x[1]):
        flag = "✗ 超 GitHub 上限" if size > HARD_LIMIT else "· 偏大"
        print(f"  {flag} {p.relative_to(root)}  {human(size)}")
    if not oversize:
        print("  没有超过 800KB 的图片")
    print()

    if args.check:
        return _summary(total_before, 0)

    print("— 压缩 —" if args.apply else "— 压缩预演（加 --apply 实际写入）—")
    total_after = 0
    saved_any = False
    for p in files:
        before, after = compress_png(p, args.apply, args.colors)
        total_after += after
        if after < before * 0.9:
            pct = (1 - after / before) * 100
            print(f"  {p.relative_to(root)}  {human(before)} → {human(after)}  -{pct:.0f}%")
            saved_any = True
    if not saved_any:
        print("  没有明显可压缩的图片")
        total_after = total_before
    print()

    return _summary(total_before, total_after, files)


def _summary(total_before: int, total_after: int, files: list[Path] | None = None) -> int:
    if files:
        after = total_after or total_before
        saved = total_before - after
        pct = saved / total_before * 100 if total_before else 0
        print(f"合计：{human(total_before)} → {human(after)}  省下 {human(saved)} ({pct:.0f}%)")
        if after > TOTAL_BUDGET:
            print(
                f"\n⚠ 图片总量 {human(after)} 仍超过建议上限 {human(TOTAL_BUDGET)}。"
                "\n  克隆速度会明显变慢，建议继续减少图片数量或降低分辨率。"
            )
        over = [p for p in files if p.stat().st_size > HARD_LIMIT]
        if over:
            print(f"\n✗ 仍有 {len(over)} 个文件超过 GitHub 100MB 单文件上限，无法推送：")
            for p in over:
                print(f"    {p}")
                print("    → 改用 Releases 附件，或降低分辨率重新导出")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
