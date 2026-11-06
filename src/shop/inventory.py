"""在庫つき注文受付（docs/design.md）。

まだ実装していない。spec テストが RED であることを確かめるためのスタブ。
"""


class Inventory:
    def register(self, sku, quantity):
        """REQ-001"""
        raise NotImplementedError

    def stock(self, sku):
        """REQ-002"""
        raise NotImplementedError

    def place_order(self, sku, quantity):
        """REQ-003 / REQ-004。拒否の方法は PRP-001 で人間の判断待ち。"""
        raise NotImplementedError

    def cancel(self, order_id):
        """REQ-005"""
        raise NotImplementedError
