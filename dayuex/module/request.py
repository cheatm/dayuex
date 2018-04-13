# encoding:utf-8
from dayuex.module.empty import *
from dayuex.module import Structure


class ReqOrder(Structure):

    __slots__ = ["accountID", "code", "qty", "price", "orderType", "bsType", "time", "info"]

    def __init__(self,
                 accountID=EMPTY_INT,
                 code=EMPTY_STR,
                 qty=EMPTY_INT,
                 price=EMPTY_INT,
                 orderType=EMPTY,
                 bsType=EMPTY,
                 time=EMPTY,
                 info=EMPTY_STR):
        self.accountID = accountID
        self.code = code
        self.qty = qty
        self.price = price
        self.orderType = orderType
        self.bsType = bsType
        self.time = time
        self.info = info


class QryOrder(Structure):

    __slots__ = ["accountID", "orderID"]

    def __init__(self, accountID=EMPTY_INT, orderID=EMPTY_INT):
        self.accountID = accountID
        self.orderID = orderID


class CancelOrder(Structure):

    __slots__ = ["accountID", "orderID"]

    def __init__(self, accountID=EMPTY_INT, orderID=EMPTY_INT):
        self.accountID = accountID
        self.orderID = orderID


class QryTrade(Structure):

    __slots__ = ["accountID", "orderID"]

    def __init__(self, accountID=EMPTY_INT, orderID=EMPTY_INT):
        self.accountID = accountID
        self.orderID = orderID


class QryCash(Structure):

    __slots__ = ["accountID"]

    def __init__(self, accountID=EMPTY_INT):
        self.accountID = accountID


class QryPosition(Structure):

    __slots__ = ["accountID", "code"]

    def __init__(self, accountID=EMPTY_INT, code=EMPTY_STR):
        self.accountID = accountID
        self.code = code


class Snapshot(Structure):

    __slots__ = ["accountID"]

    def __init__(self, accountID=EMPTY_INT):
        self.accountID = accountID


__all__ = ["ReqOrder", "CancelOrder", "QryOrder", "QryCash", "QryPosition", "QryTrade", "Snapshot"]