"""出自: proposed（PRP-001 候補A: 例外を投げる）。人間の承認前なのでメインのスイートに入れない。"""
import unittest

from shop.inventory import Inventory


class TestRejectStyleA(unittest.TestCase):
    # T-005 proposal PRP-001（候補A）
    def test_reject_raises_out_of_stock_error(self):
        from shop.inventory import OutOfStockError  # 候補Aが採用されたら定義する

        inv = Inventory()
        inv.register("SKU-A", 1)
        with self.assertRaises(OutOfStockError):
            inv.place_order("SKU-A", 2)


if __name__ == "__main__":
    unittest.main()
