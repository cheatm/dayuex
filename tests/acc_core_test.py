import unittest
from dayuex.server.core.account import Account
from dayuex.module import storage, request, enums
from datetime import datetime


class TextAccountCore(unittest.TestCase):

    def setUp(self):
        self.unit = 10**4
        self.id = 1367
        self.account = Account(
            self.id,
            storage.Cash(self.id, self.price(1000000)),
            {"000001": storage.Position(self.id, "000001", 1000, 1000)},
            buy_rate=5*(0.1**4), sell_rate=5*(0.1**4)
        )

    def price(self, value):
        return int(self.unit*value)

    def sell_req(self):
        price = self.price(20.34)
        req = request.ReqOrder(
            self.id, "000001", 700, price, enums.OrderType.LIMIT, enums.BSType.SELL, datetime.now()

        )
        return self.account.on_req_order(req)

    def test_sell(self):
        price = self.price(20.34)
        position = self.account._positions["000001"]
        available = self.account._cash.available
        order = self.sell_req()
        self.assertEqual(position.frozen, 700)
        trade = storage.Trade(self.account, order.orderID, 2, "000001", 700, price, order.orderType, order.bsType)
        self.account.on_trade(trade)
        self.assertEqual(self.account._cash.available, available+700*price-trade.fee)
        self.order = order

    def test_sell_overReq(self):
        self.test_sell()
        position = self.account._positions["000001"]
        req = request.ReqOrder(
            self.id, "000001", 700, self.price(20.34), enums.OrderType.LIMIT, enums.BSType.SELL, datetime.now()
        )
        order = self.account.on_req_order(req)
        self.assertEqual(order.canceled, 700)
        self.assertEqual(position.available, 300)
        self.assertEqual(position.todaySell, 700)

    def buy_req(self):
        price = self.price(10.5)
        req = request.ReqOrder(self.id, "000002", 1000, price,
                               enums.OrderType.LIMIT, enums.BSType.BUY, datetime.now())
        self.order = self.account.on_req_order(req)

    def test_buy(self):
        available = self.account._cash.available
        self.buy_req()
        self.assertEqual(self.account._cash.available, available-self.order.frzAmt-self.order.frzFee)
        trade1 = storage.Trade(self.id, self.order.orderID, 0, self.order.code, 500, self.price(10.4),
                               self.order.orderType, self.order.bsType, time=datetime.now())
        self.account.on_trade(trade1)
        position = self.account._positions.get(trade1.code)
        self.assertEqual(position.today, trade1.qty)
        trade2 = storage.Trade(self.id, self.order.orderID, 0, self.order.code, 500, self.price(10.5),
                               self.order.orderType, self.order.bsType, time=datetime.now())
        result = self.account.on_trade(trade2)
        self.assertTrue(result)
        self.assertEqual(self.order.orderStatus, enums.OrderStatus.FILLED)
        self.assertEqual(self.account._cash.available,
                         available-trade1.fee-trade1.qty*trade1.price-trade2.fee-trade2.qty*trade2.price)

    def test_buy_overpriced(self):
        available = self.account._cash.available
        self.buy_req()
        self.assertEqual(self.account._cash.available, available-self.order.frzAmt-self.order.frzFee)
        trade1 = storage.Trade(self.id, self.order.orderID, 0, self.order.code, 500, self.price(10.5),
                               self.order.orderType, self.order.bsType, time=datetime.now())
        self.account.on_trade(trade1)
        position = self.account._positions.get(trade1.code)
        self.assertEqual(position.today, trade1.qty)
        p = position.today
        cq = self.order.cumQty
        trade2 = storage.Trade(self.id, self.order.orderID, 0, self.order.code, 500, self.price(10.6),
                               self.order.orderType, self.order.bsType, time=datetime.now())
        result = self.account.on_trade(trade2)
        self.assertFalse(result)
        self.assertEqual(p, position.today)
        self.assertEqual(cq, self.order.cumQty)

    def test_cancel(self):
        available = self.account._cash.available
        self.buy_req()
        order = self.account.on_cancel(request.CancelOrder(self.id, self.order.orderID))
        self.assertEqual(available, self.account._cash.available)
        self.assertEqual(order.unfilled, 0)

        position = self.account._positions["000001"]
        available = position.available
        order = self.sell_req()
        canceled = self.account.on_cancel(request.CancelOrder(self.id, order.orderID))
        self.assertEqual(position.available, available)
        self.assertEqual(canceled.unfilled, 0)

        result = self.account.on_cancel(request.CancelOrder(self.id, 30))
        self.assertEqual(result.reason, enums.CanceledReason.MISSING)


if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestSuite()
    # suite.addTest(TextAccountCore("test_cancel"))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)