"""出自: spec（docs/design.md 由来）。各テストの covers は trace.json に記録する。"""
import unittest

from shop.inventory import Inventory


class TestRegister(unittest.TestCase):
    # T-001 covers REQ-001, REQ-002
    def test_register_and_query_stock(self):
        inv = Inventory()
        inv.register("SKU-A", 10)
        self.assertEqual(inv.stock("SKU-A"), 10)
        inv.register("SKU-A", 3)
        self.assertEqual(inv.stock("SKU-A"), 3)


class TestOrder(unittest.TestCase):
    def setUp(self):
        self.inv = Inventory()
        self.inv.register("SKU-A", 10)

    # T-002 covers REQ-003
    def test_place_order_within_stock_reduces_stock(self):
        order_id = self.inv.place_order("SKU-A", 10)
        self.assertIsNotNone(order_id)
        self.assertEqual(self.inv.stock("SKU-A"), 0)

    # T-003 covers REQ-004
    # 拒否の方法は未規定（PRP-001）なので、どの方法でも成り立つ「在庫が変わらない」だけを確かめる。
    def test_rejected_order_keeps_stock(self):
        try:
            self.inv.place_order("SKU-A", 11)
        except NotImplementedError:
            raise
        except Exception:
            pass
        self.assertEqual(self.inv.stock("SKU-A"), 10)

    # T-004 covers REQ-005
    def test_cancel_returns_stock(self):
        order_id = self.inv.place_order("SKU-A", 4)
        self.inv.cancel(order_id)
        self.assertEqual(self.inv.stock("SKU-A"), 10)


if __name__ == "__main__":
    unittest.main()
