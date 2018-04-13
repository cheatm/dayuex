

class Structure:

    __slots__ = []

    def __str__(self):
        return "{}({})" .format(
            self.__class__.__name__,
            ', '.join(["{}={}".format(attr, self.__getattribute__(attr)) for attr in self.__slots__])
        )
    