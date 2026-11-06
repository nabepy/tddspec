# 引き継ぎメモ（handoff）

## 今のフェーズ
- 試作: サンプル設計書と 要求 × テスト マトリクス（2026-11-06）。
- 設計書 `docs/design.md`（在庫つき注文受付, REQ-001〜006）を置き、`trace.json` に要求を登録した。
- 実装は `src/shop/inventory.py` のスタブのみ。テストはすべて RED（Red フェーズ）。
  - spec: T-001〜T-004, T-007（REQ-001〜005 をカバー）。REQ-006 は spec 未着手（マトリクスで灰）。
  - proposed: T-005（PRP-001 候補A: 例外）。改訂後の REQ-004 と矛盾するため suspect を付けた。
  - explore: T-006（数量0の注文）。
- テストの実行: `python3 run_tests.py`（spec + explore）、`python3 run_tests.py proposed`（提案のみ）。
- マトリクス: `python3 viz/build_matrix.py` → `viz/matrix.html`。

## 承認待ちの提案
- PRP-001: 在庫を超える注文の扱い。nabepy が候補C（在庫数分を提供し、残りは納期予定を提示して確認を求める）を出し、
  2026-11-06 に設計書の REQ-004 をこの案で改訂した。承認の記録（chosen / reason / approved_by）は人間が書く。
  承認されたら T-005 を削除し、PRP-001 を approved にする。
- PRP-002: REQ-004 の納期予定の決め方。候補A=商品ごとの入荷予定日、候補B=注文日＋一定日数。

## 設計の余白（REQ-004 改訂で新たに出たもの）
- 顧客が提示を承諾しなかったときの扱い、残りの数量の入荷時の引き当て、一部提供した注文のキャンセル。

## 次の一手
1. 人間が PRP-001（候補C）の承認を記録し、PRP-002 の候補を選ぶ。
2. REQ-006 の spec RED テストを書く。
3. spec を GREEN にする実装に進む（納期予定の決め方は PRP-002 の決定後）。

## trace.json の任意フィールド（このフェーズで追加）
- テストの `relates`: 関連する要求ID。`covers` と違いカバー扱いにしない（proposed / explore 用）。
- テストの `suspect`: 逸脱疑いの理由。マトリクスで赤になる。
- 提案の `requirement`: 対象の要求ID。
- テストの `description`: 何を確かめるかの日本語の説明。マトリクスの列見出しに表示する。
