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
        """REQ-003 / REQ-004。在庫を超える注文は提示（offer）を返す。納期予定の決め方は PRP-002。"""
        raise NotImplementedError

    def confirm(self, offer):
        """REQ-004。顧客が提示を承諾したときに呼ぶ。"""
        raise NotImplementedError

    def cancel(self, order_id):
        """REQ-005"""
        raise NotImplementedError
