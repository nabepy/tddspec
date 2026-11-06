#!/usr/bin/env python3
"""メインのテストスイート（tests/spec と tests/explore）を実行する。tests/proposed は含めない。

  python3 run_tests.py             spec と explore
  python3 run_tests.py proposed    承認前の提案テストだけを個別に試す
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

dirs = sys.argv[1:] or ["spec", "explore"]
suite = unittest.TestSuite()
for d in dirs:
    suite.addTests(unittest.defaultTestLoader.discover(str(ROOT / "tests" / d)))
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
