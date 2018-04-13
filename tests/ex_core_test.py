import unittest
from dayuex.server.core.exchange import ExchangeCore
from dayuex.module.storage import Order
from dayuex.module.enums import OrderType, BSType


class TestExchangeCore(unittest.TestCase):

    def setUp(self):
        self.exchange = ExchangeCore()
        self.tick = {
            'date': 20171018,
            'code': '300667.XSHE',
            'ask': [[46.4, 2600], [46.41, 600], [46.42, 1300], [46.43, 2900], [46.44, 200]],
            'time': 94109000,
            'bid': [[46.39, 200], [46.29, 1000], [46.28, 400], [46.2, 300], [46.19, 600]]
        }
        self.order_buy = Order(orderID=0, code='300667.XSHE', qty=4000, price=46.42,
                               orderType=OrderType.LIMIT, bsType=BSType.BUY)
        self.order_sell = Order(orderID=1, code='300667.XSHE', qty=2000, price=46.27,
                                orderType=OrderType.LIMIT, bsType=BSType.SELL)

    def test_buy(self):
        self.exchange.on_order(self.order_buy)
        amount = 0
        for trade in self.exchange.on_tick(self.tick):
            amount += trade.price * trade.qty
        self.assertEqual(amount, 148486)
        self.assertEqual(self.order_buy.unfilled, 0)

    def test_sell(self):
        self.exchange.on_order(self.order_sell)
        amount = 0
        for trade in self.exchange.on_tick(self.tick):
            amount += trade.price * trade.qty
        self.assertEqual(amount, 74080)
        self.assertEqual(self.order_sell.unfilled, 400)


if __name__ == '__main__':
    unittest.main()