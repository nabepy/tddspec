# tddspec

人間が書いた設計書に基づいて AI に実装・テストしてもらうための TDD 枠組み。

- 設計書（サンプル）: `docs/design.md`
- テスト実行: `python3 run_tests.py`（spec + explore。proposed は含めない）
- 出自タグの検査: `python3 check_tags.py`
- 要求 × テスト マトリクス: `python3 viz/build_matrix.py` → `viz/matrix.html`
