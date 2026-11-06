#!/usr/bin/env python3
"""TDD出自タグの検査。

使い方:
  python3 check_tags.py            検査する（違反があれば終了コード1）
  python3 check_tags.py --hook     Stopフック用（違反があれば終了コード2でClaudeに差し戻す）
  python3 check_tags.py --summary  SessionStartフック用の要約を出力する
"""
import fnmatch
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
TRACE = ROOT / "trace.json"
TEST_ROOT = "tests"
TAG_DIRS = {
    "spec": "tests/spec",
    "proposed": "tests/proposed",
    "explore": "tests/explore",
}
TEST_PATTERNS = ("test_*", "*_test.*", "*.test.*", "*.spec.*", "*Tests.swift", "*Test.swift")
SKIP_DIRS = {"__pycache__", "node_modules", ".pytest_cache"}
TEST_STATUS = {"red", "green"}
PROPOSAL_STATUS = {"pending", "approved", "rejected"}


def load():
    try:
        return json.loads(TRACE.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, "missing"
    except json.JSONDecodeError as e:
        return None, f"trace.json が不正なJSONです: {e}"


def disk_tests():
    base = ROOT / TEST_ROOT
    found = set()
    if not base.exists():
        return found
    for p in base.rglob("*"):
        if not p.is_file() or SKIP_DIRS & set(p.parts):
            continue
        if any(fnmatch.fnmatch(p.name, pat) for pat in TEST_PATTERNS):
            found.add(p.relative_to(ROOT).as_posix())
    return found


def check(data):
    errors, warnings = [], []
    reqs = {r.get("id") for r in data.get("requirements", []) if r.get("id")}
    props = {p.get("id"): p for p in data.get("proposals", [])}
    tests = data.get("tests", [])
    registered = set()

    for t in tests:
        tid = t.get("id", "?")
        tag = t.get("tag")
        f = t.get("file", "")
        registered.add(f)
        if tag not in TAG_DIRS:
            errors.append(f"{tid}: タグが不正です（{tag}）。spec / proposed / explore のいずれかにする")
            continue
        if t.get("status") not in TEST_STATUS:
            errors.append(f"{tid}: status は red か green にする")
        if not f.startswith(TAG_DIRS[tag] + "/"):
            errors.append(f"{tid}: {tag} のテストは {TAG_DIRS[tag]}/ に置く（現在: {f}）")
        elif not (ROOT / f).exists():
            errors.append(f"{tid}: ファイルがありません: {f}")
        if tag == "spec":
            covers = t.get("covers") or []
            if not covers:
                errors.append(f"{tid}: spec には covers（要求ID）が必須")
            for c in covers:
                if c not in reqs:
                    errors.append(f"{tid}: 存在しない要求ID {c}")
        if tag == "proposed":
            p = props.get(t.get("proposal"))
            if p is None:
                errors.append(f"{tid}: proposed には有効な proposal ID が必須")
            elif p.get("status") == "approved":
                errors.append(f"{tid}: 提案 {p.get('id')} は承認済み。spec へ昇格すること")
            elif p.get("status") == "rejected":
                errors.append(f"{tid}: 提案 {p.get('id')} は却下済み。テストを削除すること")

    for f in sorted(disk_tests() - registered):
        errors.append(
            f"trace.json に未登録のテスト: {f}（出自タグを付けて登録し、tests/<tag>/ に置く）"
        )

    for pid, p in props.items():
        st = p.get("status")
        if st not in PROPOSAL_STATUS:
            errors.append(f"{pid}: 提案の status は pending / approved / rejected のいずれか")
        if st == "approved" and not (p.get("chosen") and p.get("reason") and p.get("approved_by")):
            errors.append(f"{pid}: 承認には chosen・reason・approved_by が必須")

    covered = {c for t in tests if t.get("tag") == "spec" for c in (t.get("covers") or [])}
    for r in sorted(reqs - covered):
        warnings.append(f"{r}: spec テストがまだありません")
    return errors, warnings


def summary(data):
    tests = data.get("tests", [])
    lines = ["[TDD出自タグ] trace.json の要約"]
    for tag in TAG_DIRS:
        ts = [t for t in tests if t.get("tag") == tag]
        red = sum(1 for t in ts if t.get("status") == "red")
        lines.append(f"- {tag}: {len(ts)}件（RED {red}件）")
    pending = [p.get("id") for p in data.get("proposals", []) if p.get("status") == "pending"]
    lines.append(f"- 承認待ちの提案: {len(pending)}件" + (f"（{', '.join(pending)}）" if pending else ""))
    reqs = {r.get("id") for r in data.get("requirements", []) if r.get("id")}
    covered = {c for t in tests if t.get("tag") == "spec" for c in (t.get("covers") or [])}
    uncovered = sorted(reqs - covered)
    if uncovered:
        lines.append(f"- spec テストが未着手の要求: {', '.join(uncovered)}")
    lines.append("不変ルール: specは人間の設計由来のみ / proposedは承認前に本流へ入れない / 承認は人間だけ")
    return "\n".join(lines)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "--hook":
        try:
            payload = json.loads(sys.stdin.read() or "{}")
        except json.JSONDecodeError:
            payload = {}
        if payload.get("stop_hook_active"):
            return 0

    data, err = load()
    if err == "missing":
        if mode == "--summary":
            print("[TDD出自タグ] trace.json がまだありません。")
            return 0
        if mode == "--hook":
            return 0
        print("trace.json がありません", file=sys.stderr)
        return 1
    if err:
        print(err, file=sys.stderr)
        return 2 if mode == "--hook" else 1

    if mode == "--summary":
        print(summary(data))
        return 0

    errors, warnings = check(data)
    for w in warnings:
        print(f"注意: {w}")
    if errors:
        print("TDD出自タグの検査に失敗しました。直してから終えてください:", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        return 2 if mode == "--hook" else 1
    print("OK: 出自タグの検査を通過しました")
    return 0


if __name__ == "__main__":
    sys.exit(main())
