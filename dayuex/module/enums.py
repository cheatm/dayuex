# encoding:utf-8
from enum import Enum


class BSType(Enum):

    NONE = -1
    SELL = 0
    BUY = 1


class OrderType(Enum):

    NONE = -1
    LIMIT = 0
    MARKET = 1


class OrderStatus(Enum):

    NONE = -1
    UNFILLED = 0
    FILLED = 1
    CANCELED = 2


class CanceledReason(Enum):

    NONE = -1
    CLIENT = 0
    CASH = 2
    POSITION = 3
    MISSING = 4
    ERROR = 5
