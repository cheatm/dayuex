# encoding:utf-8
from dayuex.module.empty import *
from dayuex.module.enums import *


class Structure:

    __slots__ = []

    def __str__(self):
        return "{}({})" .format(
            self.__class__.__name__,
            ', '.join(["{}={}".format(attr, self.__getattribute__(attr)) for attr in self.__slots__])
        )


class Cash(Structure):

    __slots__ = ["accountID", "available", "frozen"]

    def __init__(self, accountID=EMPTY_INT, available=EMPTY_INT, frozen=EMPTY_INT):
        self.accountID = accountID
        self.available = available
        self.frozen = frozen

    def freeze(self, num):
        if self.available >= num:
            self.available -= num
            self.frozen += num
        else:
            raise CashFreezeExceed(self.accountID, self.available, num)

    def unfreeze(self, num):
        if self.frozen >= num:
            self.available += num
            self.frozen -= num
        else:
            raise CashUnfreezeExceed(self.accountID, self.frozen, num)

    def add(self, num):
        self.available += num

    def sub(self, num):
        if self.frozen >= num:
            self.frozen -= num
        else:
            raise CashSubExceed(self.accountID, self.available, self.frozen, num)


class CashFreezeExceed(Exception):

    def __init__(self, accountID, available, freeze):
        self.accountID = accountID
        self.available = available
        self.freeze = freeze


class CashUnfreezeExceed(Exception):

    def __init__(self, accountID, frozen, unfreeze):
        self.accountID = accountID
        self.frozen = frozen
        self.unfreeze = unfreeze


class CashSubExceed(Exception):

    def __init__(self, accountID, available, frozen, sub):
        self.accountID = accountID
        self.available = available
        self.frozen = frozen
        self.sub = sub


class Order(Structure):

    __slots__ = ["accountID", "orderID", "code", "qty", "cumQty", "price", "orderType", "bsType", "orderStatus",
                 "frzAmt", "frzFee", "cumAmt", "cumFee",  "canceled", "reason", "time", "cnfmTime"]

    def __init__(self,
                 accountID=EMPTY_INT,
                 orderID=EMPTY_INT,
                 code=EMPTY_STR,
                 qty=EMPTY_INT,
                 cumQty=EMPTY_INT,
                 price=EMPTY_FLOAT,
                 orderType=OrderType.LIMIT,
                 bsType=BSType.BUY,
                 orderStatus=OrderStatus.UNFILLED,
                 frzAmt=EMPTY_INT,
                 frzFee=EMPTY_INT,
                 cumAmt=EMPTY_INT,
                 cumFee=EMPTY_INT,
                 canceled=EMPTY_INT,
                 reason=CanceledReason.NONE,
                 time=EMPTY,
                 cnfmTime=EMPTY):
        self.accountID = accountID
        self.orderID = orderID
        self.code = code
        self.qty = qty
        self.cumQty = cumQty
        self.price = price
        self.orderType = orderType
        self.bsType = bsType
        self.frzAmt = frzAmt
        self.frzFee = frzFee
        self.cumAmt = cumAmt
        self.cumFee = cumFee
        self.canceled = canceled
        self.reason = reason
        self.orderStatus = orderStatus
        self.time = time
        self.cnfmTime = cnfmTime

    @property
    def unfilled(self):
        return self.qty - self.cumQty - self.canceled


class Trade(Structure):
    __slots__ = ["accountID", "orderID", "tradeID", "code", "qty", "price", "orderType", "bsType", "fee",
                 "orderStatus", "time"]

    def __init__(self,
                 accountID=EMPTY_STR,
                 orderID=EMPTY_INT,
                 tradeID=EMPTY_INT,
                 code=EMPTY_STR,
                 qty=EMPTY_INT,
                 price=EMPTY_INT,
                 orderType=OrderType.LIMIT,
                 bsType=BSType.BUY,
                 fee=EMPTY_INT,
                 orderStatus=OrderStatus.UNFILLED,
                 time=EMPTY
                 ):
        self.accountID = accountID
        self.orderID = orderID
        self.tradeID = tradeID
        self.code = code
        self.qty = qty
        self.price = price
        self.orderType = orderType
        self.bsType = bsType
        self.fee = fee
        self.orderStatus = orderStatus
        self.time = time

    def __eq__(self, other):
        return self.accountID == other.accountID


class Position(Structure):

    __slots__ = ["accountID", "code", "origin", "available", "frozen", "today", "todaySell"]

    def __init__(self,
                 accountID=EMPTY_STR,
                 code=EMPTY_STR,
                 origin=EMPTY_INT,
                 available=EMPTY_INT,
                 frozen=EMPTY_INT,
                 today=EMPTY_INT,
                 todaySell=EMPTY_INT,
                 ):
        self.accountID = accountID
        self.code = code
        self.origin = origin
        self.available = available
        self.frozen = frozen
        self.today = today
        self.todaySell = todaySell

    def freeze(self, qty):
        if self.available >= qty:
            self.available -= qty
            self.frozen += qty
        else:
            raise PositionFreezeExceed(self.accountID, self.code, self.available, qty)

    def unfreeze(self, qty):
        if self.frozen >= qty:
            self.available += qty
            self.frozen -= qty
        else:
            raise PositionFreezeExceed(self.accountID, self.code, self.frozen, qty)

    def add(self, qty):
        self.today += qty

    def sub(self, qty):
        if self.frozen >= qty:
            self.frozen -= qty
            self.todaySell += qty
        else:
            raise PositionSubExceed(self.accountID, self.code, self.frozen, qty)

    def day_off(self):
        self.available += self.frozen + self.today
        self.frozen = 0
        self.today = 0
        self.origin = self.available

class PositionFreezeExceed(Exception):

    def __init__(self, accountID, code, available, qty):
        self.accountID = accountID
        self.code = code
        self.available = available
        self.qty = qty


class PositionUnfreezeExceed(Exception):

    def __init__(self, accountID, code, frozen, qty):
        self.accountID = accountID
        self.code = code
        self.frozen = frozen
        self.qty = qty


class PositionSubExceed(PositionUnfreezeExceed): pass