# 引き継ぎメモ（handoff）

## 今のフェーズ
- 試作: サンプル設計書と 要求 × テスト マトリクス（2026-11-06）。
- 設計書 `docs/design.md`（在庫つき注文受付, REQ-001〜006）を置き、`trace.json` に要求を登録した。
- 実装は `src/shop/inventory.py` のスタブのみ。テストはすべて RED（Red フェーズ）。
  - spec: T-001〜T-004（REQ-001〜005 をカバー）。REQ-006 は spec 未着手（マトリクスで灰）。
  - proposed: T-005（PRP-001 候補A）。メインのスイートには入れない。
  - explore: T-006（数量0の注文）、T-007（在庫不足時の部分受付）。
- テストの実行: `python3 run_tests.py`（spec + explore）、`python3 run_tests.py proposed`（提案のみ）。
- マトリクス: `python3 viz/build_matrix.py` → `viz/matrix.html`。

## 承認待ちの提案
- PRP-001: REQ-004 の「拒否する」の方法が未規定。候補A=OutOfStockError 例外、候補B=結果オブジェクトを返す。人間の判断待ち。

## 逸脱疑い（人間に報告）
- T-007（explore）は在庫不足時に部分的に受け付けることを期待しており、REQ-004 と矛盾する。spec を優先する。
  マトリクスの赤表示を確かめるためのサンプルとして意図的に置いた。削除するか、REQ-004 を見直すかは人間が決める。

## 次の一手
1. 人間が PRP-001 の候補を選ぶ（または候補を差し戻す）。
2. T-007 の扱いを人間が決める。
3. REQ-006 の spec RED テストを書く。
4. spec を GREEN にする実装に進む（拒否の方法は PRP-001 の決定後）。

## trace.json の任意フィールド（このフェーズで追加）
- テストの `relates`: 関連する要求ID。`covers` と違いカバー扱いにしない（proposed / explore 用）。
- テストの `suspect`: 逸脱疑いの理由。マトリクスで赤になる。
- 提案の `requirement`: 対象の要求ID。
