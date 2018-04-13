from dayuex.module.storage import Cash, Order, Position
from dayuex.module.enums import OrderStatus, BSType, CanceledReason
import logging


class AccountOrderIDGenerator(object):

    def __init__(self, accountID, ps_log=6):
        self.accountID = accountID
        self.ps_log = ps_log
        self.time_expand = 2**ps_log
        self.head = self.accountID*(2**32)*self.time_expand
        self.last = 0

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        last = self.head + int(datetime.now().timestamp()*self.time_expand)
        if last > self.last:
            self.last = last
            return last
        else:
            self.last += 1
            return self.last


class Account(object):

    def __init__(self, accountID=0, cash=None, positions=None, orders=None, trades=None, buy_rate=0, sell_rate=0):
        self.accountID = accountID
        self._cash = cash if isinstance(cash, Cash) else Cash()
        self._cash.accountID = self.accountID
        self._positions = positions if positions else {}
        self._orders = orders if orders else {}
        self._trades = trades if trades else {}
        self.br = buy_rate
        self.sr = sell_rate
        self._id = AccountOrderIDGenerator(self.accountID)

    def on_req_order(self, req):
        if req.bsType == BSType.BUY:
            order = create_order(req, self._id.next(), self.br)
            return self._atomic_buy_order(order)
        else:
            order = create_order(req, self._id.next(), self.sr)
            return self._atomic_sell_order(order)

    def _atomic_buy_order(self, order):
        total_frz = order.frzAmt + order.frzFee
        if total_frz > self._cash.available:
            order.canceled = order.unfilled
            order.frzAmt = 0
            order.frzFee = 0
            order.reason = CanceledReason.CASH
        else:
            self._cash.freeze(total_frz)
            self._orders[order.orderID] = order
        return order

    def _atomic_sell_order(self, order):
        position = self._positions.get(order.code, None)

        if isinstance(position, Position) and (order.qty <= position.available):
            position.freeze(order.qty)
            self._orders[order.orderID] = order
        else:
            order.canceled = order.unfilled
            order.reason = CanceledReason.POSITION

        return order

    def on_cancel(self, cancel):
        try:
            order = self._orders[cancel.orderID]
        except KeyError:
            logging.error("cancel | %s | order not found", cancel)
            return Order(self.accountID, reason=CanceledReason.MISSING)

        if order.bsType.value == BSType.BUY.value:
            value = order.frzAmt-order.cumFee+order.frzFee-order.cumFee
            self._cash.unfreeze(value)
        else:
            position = self._positions.get(order.code)
            position.unfreeze(order.unfilled)
        self._cancel(order)
        return order

    @staticmethod
    def _cancel(order):
        order.canceled = order.unfilled
        order.reason = CanceledReason.CLIENT

    def on_trade(self, trade):
        order = self._orders.get(trade.orderID, None)
        if order is None:
            logging.error("on trade | buy | %s | order not found", trade)
            return False
        if order.bsType.value == BSType.BUY.value:
            try:
                trade.fee = int(trade.price*trade.qty*self.br)
                return self._atomic_buy_trade(order, trade)
            except Exception as e:
                logging.error("on trade | buy | %s | %s | %s", trade, order, e)
                return False
        else:
            try:
                return self._atomic_sell_trade(order, trade)
            except Exception as e:
                trade.fee = int(trade.price*trade.qty*self.sr)
                logging.error("on trade | sell | %s | %s | %s", trade, order, e)
                return False

    def _atomic_buy_trade(self, order, trade):
        qty, fee, amt = self._check_trade(order, trade)

        self._cash.sub(trade.fee + trade.qty * trade.price)

        # ========================== check complete ========================== #

        position = self._positions.get(trade.code, None)
        if position is None:
            position = Position(self.accountID, trade.code)
            self._positions[trade.code] = position
        position.add(trade.qty)

        order.cumQty = qty
        order.cumFee = fee
        order.cumAmt = amt

        if order.unfilled == 0:
            order.orderStatus = OrderStatus.FILLED
            self._cash.unfreeze(order.frzAmt-order.cumAmt+order.frzFee-order.cumFee)
        return True

    def _atomic_sell_trade(self, order, trade):
        qty, fee, amt = self._check_trade(order, trade)
        position = self._positions.get(trade.code)
        position.sub(trade.qty)
        # ========================== check complete ========================== #
        self._cash.add(trade.qty * trade.price - trade.fee)
        order.cumFee = fee
        order.cumAmt = amt
        order.cumQty = qty
        if order.unfilled == 0:
            order.orderStatus = OrderStatus.FILLED
        return True

    @staticmethod
    def _check_trade(order, trade):
        qty = order.cumQty + trade.qty
        fee = order.cumFee + trade.fee
        amt = order.cumAmt + trade.qty * trade.price
        for limit, value in [(order.qty, qty), (order.frzFee, fee), (order.frzAmt, amt)]:
            if value > limit:
                raise ValueError("{} > {}".format(value, limit))
        return qty, fee, amt

    def on_qry_order(self, qry):
        return self._orders[qry.orderID]

    def on_qry_trade(self, qry):
        return self._trades[qry.orderID]

    def on_qry_cash(self, qry):
        return self._cash

    def on_qry_position(self, qry):
        return self._positions[qry.code]

    def on_snapshot(self):
        pass


from datetime import datetime


def create_order(req, order_id, fee_rate):
    return Order(req.accountID, order_id, req.code, req.qty,
                 price=req.price, orderType=req.orderType, bsType=req.bsType,
                 frzAmt=req.price*req.qty, frzFee=int(req.price*req.qty*fee_rate),
                 time=req.time, cnfmTime=datetime.now())

