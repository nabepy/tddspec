"""出自: explore（設計が未規定の境界値を古典的TDDで探索する）。"""
import unittest

from shop.inventory import Inventory


class TestOrderBoundary(unittest.TestCase):
    def setUp(self):
        self.inv = Inventory()
        self.inv.register("SKU-A", 5)

    # T-006 数量0の注文は、在庫を変えずに受け付けない（未規定。探索で挙動を固める）
    def test_zero_quantity_does_not_change_stock(self):
        try:
            self.inv.place_order("SKU-A", 0)
        except NotImplementedError:
            raise
        except Exception:
            pass
        self.assertEqual(self.inv.stock("SKU-A"), 5)


if __name__ == "__main__":
    unittest.main()
