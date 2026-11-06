# 引き継ぎメモ（handoff）

## 今のフェーズ
- 枠組みの設置が完了した直後（2026-11-06）。
- `CLAUDE.md`・`trace.json`・`check_tags.py`・`.claude/settings.json`（SessionStart/Stop フック）を配置した。
- `tests/spec`・`tests/proposed`・`tests/explore` は空（`.gitkeep` のみ）。
- 設計書はまだなく、`trace.json` の要求（requirements）・テスト・提案はいずれも0件。

## 承認待ちの提案
- なし。

## 次の一手
1. 人間が要求ID（REQ-xxx）付きの設計書を用意する。
2. 設計書の要求を `trace.json` の `requirements` に登録する。
3. 要求ごとに spec の RED テストを `tests/spec/` に書き、`covers` に要求IDを付けて登録する。
4. 設計書にない挙動が必要になったら、`proposals` に候補2〜3と根拠を登録して人間の判断を待つ。
5. 作業の最後に `python3 check_tags.py` を実行して通ることを確認する。

## 今後の検討（参考）
- 要求ID × テストのトレーサビリティマトリクスによる可視化（未カバー・設計書外・逸脱疑いの色分け）。
