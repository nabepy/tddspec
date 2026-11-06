#!/usr/bin/env python3
"""trace.json から 要求 × テスト のマトリクスを1枚のHTMLに書き出す。

使い方:
  python3 viz/build_matrix.py                 viz/matrix.html に出力
  python3 viz/build_matrix.py -o out.html     出力先を指定

色の意味:
  灰  = spec テストがまだない要求（未カバー）
  橙  = 要求に紐づかないテスト（proposed / explore）
  赤  = 逸脱疑い（テストの suspect に理由が書かれている）
  セル ● = covers（spec がカバー）, ○ = relates（関連するだけでカバー扱いにしない）
"""
import argparse
import html
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAG_LABEL = {"spec": "spec", "proposed": "proposed", "explore": "explore"}

CSS = """
:root{--bg:#fff;--fg:#1f2328;--muted:#656d76;--line:#d0d7de;--head:#f6f8fa;
--gray:#e6e8eb;--gray-fg:#57606a;--orange:#fff1e0;--orange-fg:#9a4b00;--orange-bd:#f0a35a;
--red:#ffe4e4;--red-fg:#b42318;--red-bd:#f08080;--green:#dcf5e3;--green-fg:#1a7f37}
@media (prefers-color-scheme:dark){:root{--bg:#0d1117;--fg:#e6edf3;--muted:#8d96a0;--line:#30363d;
--head:#161b22;--gray:#21262d;--gray-fg:#8d96a0;--orange:#3a2410;--orange-fg:#f5b26b;--orange-bd:#9a5a1a;
--red:#3d1416;--red-fg:#ff8a80;--red-bd:#a33a3a;--green:#12301d;--green-fg:#5fd38a}}
*{box-sizing:border-box}
body{margin:0;padding:24px 16px;background:var(--bg);color:var(--fg);
font:14px/1.5 system-ui,-apple-system,"Hiragino Sans","Noto Sans JP",sans-serif}
main{max-width:1100px;margin:0 auto}
h1{font-size:20px;margin:0 0 4px}h2{font-size:16px;margin:28px 0 8px}
.muted{color:var(--muted)}
.stats{display:flex;flex-wrap:wrap;gap:8px;margin:16px 0}
.stat{border:1px solid var(--line);border-radius:8px;padding:8px 12px;min-width:120px}
.stat b{display:block;font-size:20px}
.legend{display:flex;flex-wrap:wrap;gap:12px;margin:8px 0 12px;font-size:13px}
.sw{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:-1px;margin-right:4px;border:1px solid var(--line)}
.wrap{overflow-x:auto;border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%}
th,td{border-bottom:1px solid var(--line);border-right:1px solid var(--line);padding:6px 8px;text-align:center;vertical-align:middle}
th{background:var(--head);font-weight:600}
th.req,td.req{text-align:left;min-width:260px;position:sticky;left:0;background:var(--bg);z-index:1}
thead th.req{background:var(--head)}
.tcol{font-size:12px;min-width:84px}
.tcol .tid{font-weight:700;font-size:13px}
.badge{display:inline-block;font-size:11px;padding:0 6px;border-radius:10px;margin-top:2px}
.st-red{background:var(--red);color:var(--red-fg)}.st-green{background:var(--green);color:var(--green-fg)}
.tag-spec{background:var(--head);color:var(--fg);border:1px solid var(--line)}
.tag-proposed,.tag-explore{background:var(--orange);color:var(--orange-fg)}
th.orphan{background:var(--orange);box-shadow:inset 0 3px 0 var(--orange-bd)}
th.suspect{background:var(--red);box-shadow:inset 0 3px 0 var(--red-bd)}
tr.uncovered td{background:var(--gray);color:var(--gray-fg)}
tr.deviation td.req{box-shadow:inset 4px 0 0 var(--red-bd)}
tr.outside td.req{background:var(--orange);color:var(--orange-fg)}
td.c-cov{font-size:16px}
td.c-rel{color:var(--muted)}
td.c-sus{background:var(--red)!important;color:var(--red-fg)}
td.c-out{background:var(--orange)}
.rid{font-weight:700;margin-right:6px}
.flag{white-space:nowrap;font-size:11px;margin-left:6px;padding:0 6px;border-radius:10px}
.flag.gray{background:var(--bg);color:var(--gray-fg);border:1px solid var(--line)}
.flag.red{background:var(--red);color:var(--red-fg)}
.flag.orange{background:var(--orange);color:var(--orange-fg)}
.card{border:1px solid var(--line);border-radius:8px;padding:12px 14px;margin:8px 0}
.card.pending{border-left:4px solid var(--orange-bd)}
.card.sus{border-left:4px solid var(--red-bd)}
.card h3{font-size:14px;margin:0 0 6px}
.cands{margin:6px 0 0;padding-left:18px}
"""


def esc(s):
    return html.escape(str(s if s is not None else ""))


def build(data):
    reqs = data.get("requirements", [])
    tests = data.get("tests", [])
    props = {p.get("id"): p for p in data.get("proposals", [])}
    req_ids = {r.get("id") for r in reqs}

    def links(t):
        cov = set(t.get("covers") or []) if t.get("tag") == "spec" else set()
        rel = set(t.get("relates") or [])
        p = props.get(t.get("proposal"))
        if p and p.get("requirement"):
            rel.add(p["requirement"])
        return cov, rel - cov

    covered = {c for t in tests for c in links(t)[0]}
    suspect_reqs = {r for t in tests if t.get("suspect") for r in set().union(*links(t))}

    # 表頭: テストの列
    head = ['<th class="req">要求 \\ テスト</th>']
    for t in tests:
        cov, rel = links(t)
        cls = "tcol"
        if t.get("suspect"):
            cls += " suspect"
        elif not cov:
            cls += " orphan"
        st = t.get("status", "?")
        title = f'{t.get("file")}::{t.get("name")}'
        head.append(
            f'<th class="{cls}" title="{esc(title)}"><div class="tid">{esc(t.get("id"))}</div>'
            f'<span class="badge tag-{esc(t.get("tag"))}">{esc(TAG_LABEL.get(t.get("tag"), t.get("tag")))}</span><br>'
            f'<span class="badge st-{esc(st)}">{esc(st).upper()}</span></th>'
        )

    rows = []
    for r in reqs:
        rid = r.get("id")
        cls, flags = [], []
        if rid not in covered:
            cls.append("uncovered")
            flags.append('<span class="flag gray">未カバー</span>')
        if rid in suspect_reqs:
            cls.append("deviation")
            flags.append('<span class="flag red">逸脱疑い</span>')
        if any(p.get("requirement") == rid and p.get("status") == "pending" for p in props.values()):
            flags.append('<span class="flag orange">承認待ちの提案</span>')
        cells = [f'<td class="req"><span class="rid">{esc(rid)}</span>{esc(r.get("text"))}{"".join(flags)}</td>']
        for t in tests:
            cov, rel = links(t)
            sus = " c-sus" if t.get("suspect") and rid in (cov | rel) else ""
            if rid in cov:
                cells.append(f'<td class="c-cov{sus}" title="covers">●</td>')
            elif rid in rel:
                cells.append(f'<td class="c-rel{sus}" title="relates">○</td>')
            else:
                cells.append(f'<td class="{sus.strip()}"></td>')
        rows.append(f'<tr class="{" ".join(cls)}">{"".join(cells)}</tr>')

    # 要求に紐づかないテスト（covers がない）をまとめる行
    out = ['<td class="req"><span class="rid">設計書外</span>要求をカバーしないテスト（proposed / explore）</td>']
    for t in tests:
        out.append('<td class="c-out">◆</td>' if not links(t)[0] else "<td></td>")
    rows.append(f'<tr class="outside">{"".join(out)}</tr>')

    # 提案と逸脱疑い
    cards = []
    for p in props.values():
        if p.get("status") != "pending":
            continue
        cands = "".join(
            f'<li><b>{esc(c.get("id"))}</b>: {esc(c.get("summary"))}'
            + (f' <span class="muted">— {esc(c.get("rationale"))}</span>' if c.get("rationale") else "")
            + (f' <span class="muted">（spec {esc(c.get("spec"))} / explore {esc(c.get("explore"))}）</span>' if c.get("spec") else "")
            + "</li>"
            for c in p.get("candidates", [])
        )
        ts = ", ".join(esc(t.get("id")) for t in tests if t.get("proposal") == p.get("id")) or "なし"
        cards.append(
            f'<div class="card pending"><h3>{esc(p.get("id"))}（{esc(p.get("requirement") or "-")}）: {esc(p.get("gap"))}</h3>'
            f'<div class="muted">状態: 承認待ち ・ 提案テスト: {ts}</div><ul class="cands">{cands}</ul></div>'
        )
    sus_cards = [
        f'<div class="card sus"><h3>{esc(t.get("id"))} {esc(t.get("name"))}</h3>'
        f'<div>{esc(t.get("suspect"))}</div><div class="muted">{esc(t.get("file"))}</div></div>'
        for t in tests if t.get("suspect")
    ]
    unknown = sorted({c for t in tests for c in (t.get("relates") or [])} - req_ids)

    n_red = sum(1 for t in tests if t.get("status") == "red")
    stats = [
        ("要求", len(reqs)),
        ("spec でカバー", f"{len(covered & req_ids)}/{len(reqs)}"),
        ("テスト", f"{len(tests)}（RED {n_red}）"),
        ("承認待ちの提案", len(cards)),
        ("逸脱疑い", len(sus_cards)),
    ]
    stat_html = "".join(f'<div class="stat"><span class="muted">{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in stats)
    legend = (
        '<span><span class="sw" style="background:var(--gray)"></span>灰: 未カバーの要求</span>'
        '<span><span class="sw" style="background:var(--orange)"></span>橙: 要求に紐づかないテスト</span>'
        '<span><span class="sw" style="background:var(--red)"></span>赤: 逸脱疑い</span>'
        '<span>● covers ・ ○ relates（カバー扱いにしない） ・ ◆ 設計書外</span>'
    )
    warn = f'<p class="flag red">trace.json にない要求ID: {esc(", ".join(unknown))}</p>' if unknown else ""

    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>要求テストマトリクス</title><style>{CSS}</style></head>
<body><main>
<h1>要求 × テスト マトリクス</h1>
<div class="muted">trace.json から生成 ・ {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
<div class="stats">{stat_html}</div>
<div class="legend">{legend}</div>{warn}
<div class="wrap"><table><thead><tr>{"".join(head)}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>
<h2>承認待ちの提案</h2>{"".join(cards) or '<p class="muted">なし</p>'}
<h2>逸脱疑い（spec を優先し、人間が判断する）</h2>{"".join(sus_cards) or '<p class="muted">なし</p>'}
</main></body></html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--trace", default=str(ROOT / "trace.json"))
    ap.add_argument("-o", "--out", default=str(ROOT / "viz" / "matrix.html"))
    a = ap.parse_args()
    data = json.loads(Path(a.trace).read_text(encoding="utf-8"))
    Path(a.out).write_text(build(data), encoding="utf-8")
    print(f"書き出しました: {a.out}")


if __name__ == "__main__":
    main()
