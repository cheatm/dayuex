from dayuex.module.storage import Trade, Order
from dayuex.module.enums import BSType, OrderType, OrderStatus
from datetime import datetime
from queue import deque
import logging
import time


CODE = "code"
VOLUME = "volume"
PRICE = "price"
ASK = "ask"
BID = "bid"
DATE = "date"
TIME = "time"
PRE = "pre"


class ExchangeCore(object):

    def __init__(self, packs=None, transactor=None):
        self._packs = packs if isinstance(packs, dict) else {}
        self.transactor = transactor if isinstance(transactor, Transactor) else Transactor()

    def on_tick(self, tick):
        code = tick[CODE]
        pack = self._get_pack(code)
        for order in pack:
            yield from self.transactor[order.bsType](order, tick)
            pack.wait(order)
        pack.recycle()

    def on_order(self, order):
        self._get_pack(order.code).put(order)

    def on_cancel(self, cancel):
        self._get_pack(cancel.code).cancel(cancel)

    def _get_pack(self, code):
        try:
            return self._packs[code]
        except KeyError:
            pack = OrderPack(code)
            self._packs[code] = pack
            return pack


class OrderPack(object):

    def __init__(self, code):
        self.code = code
        self._orders = deque()
        self._wait = deque()

    def __iter__(self):
        while self._orders.__len__():
            yield self._orders.popleft()

    def recycle(self):
        while self._wait.__len__():
            order = self._wait.pop()
            self._orders.appendleft(order)

    def wait(self, order):
        if order.unfilled > 0:
            self._wait.append(order)

    def put(self, order):
        self._orders.append(order)

    def cancel(self, order):
        try:
            self._orders.remove(order)
        except:
            try:
                self._wait.remove(order)
            except:
                logging.error("cancel order | %s | fail", order)


class Transactor(object):

    def __init__(self, ids=None):
        self.ids = ids if hasattr(ids, "next") else TimerIDGenerator.year()
        self.funcs = {BSType.BUY.value: self.buy,
                      BSType.SELL.value: self.sell}

    def __getitem__(self, item):
        return self.funcs[item.value]

    def buy(self, order, tick):
        for price, volume in tick[ASK]:
            if order.price >= price and (order.unfilled > 0):
                if order.unfilled <= volume:
                    order.cumQty = order.qty
                    yield Trade(
                        order.accountID, order.orderID, self.ids.next(), order.code, order.unfilled, price,
                        order.orderType, order.bsType, 0, OrderStatus.FILLED.value, combine(tick[DATE], tick[TIME])
                    )
                else:
                    order.cumQty += volume
                    yield Trade(
                        order.accountID, order.orderID, self.ids.next(), order.code, volume, price,
                        order.orderType, order.bsType, 0, OrderStatus.FILLED.value, combine(tick[DATE], tick[TIME])
                    )
            else:
                return

    def sell(self, order, tick):
        for price, volume in tick[BID]:
            if order.price <= price and (order.unfilled > 0):
                if order.unfilled <= volume:
                    order.cumQty = order.qty
                    yield Trade(
                        order.accountID, order.orderID, self.ids.next(), order.code, order.unfilled, price,
                        order.orderType, order.bsType, 0, OrderStatus.FILLED.value, combine(tick[DATE], tick[TIME])
                    )
                else:
                    order.cumQty += volume
                    yield Trade(
                        order.accountID, order.orderID, self.ids.next(), order.code, volume, price,
                        order.orderType, order.bsType, 0, OrderStatus.FILLED.value, combine(tick[DATE], tick[TIME])
                    )
            else:
                return


def combine(date, time):
    day = date % 100
    month = int((date - day) % 10000 / 100)
    year = int(date/10000)
    ms = time % 1000
    time = time-ms
    second = int((time % 100000)/1000)
    time = time - second
    minute = int(time % 10000000 / 100000)
    hour = int(time / 10000000)
    return datetime(year, month, day, hour, minute, second, ms*1000)


class TimerIDGenerator(object):

    def __init__(self, timestamp, multiple=100):
        self.last = 0
        self.multiple = multiple
        self.origin = int(timestamp * self.multiple)

    @classmethod
    def year(cls):
        from datetime import date

        return cls(time.mktime(date.today().replace(month=1, day=1).timetuple()))

    def __next__(self):
        return self.next()

    def next(self):
        num = int(time.time()*self.multiple) - self.origin
        if num > self.last:
            self.last = num
        else:
            self.last += 1

        return self.last
