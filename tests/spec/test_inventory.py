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
    # 在庫を超える注文は、在庫数分と残り（納期予定つき）を提示するだけで、在庫はまだ変えない。
    def test_short_order_presents_offer_without_changing_stock(self):
        offer = self.inv.place_order("SKU-A", 13)
        self.assertEqual(offer.available, 10)
        self.assertEqual(offer.backorder, 3)
        self.assertIsNotNone(offer.expected_date)  # 決め方は PRP-002 で人間の判断待ち
        self.assertEqual(self.inv.stock("SKU-A"), 10)

    # T-007 covers REQ-004
    # 提示を顧客が承諾すると、注文IDが返り、在庫数分が引き当てられて在庫が0になる。
    def test_confirmed_short_order_fills_available_stock(self):
        offer = self.inv.place_order("SKU-A", 13)
        order_id = self.inv.confirm(offer)
        self.assertIsNotNone(order_id)
        self.assertEqual(self.inv.stock("SKU-A"), 0)

    # T-004 covers REQ-005
    def test_cancel_returns_stock(self):
        order_id = self.inv.place_order("SKU-A", 4)
        self.inv.cancel(order_id)
        self.assertEqual(self.inv.stock("SKU-A"), 10)


if __name__ == "__main__":
    unittest.main()
