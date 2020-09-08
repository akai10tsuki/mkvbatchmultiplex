""" TracksOrder """

class TracksOrder:
    """
     TracksOrder
    """

    def __init__(self, tracksOrder=None):

        self.__index = 0

        if tracksOrder is not None:
            self.order = tracksOrder

    def _initVars(self):

        self.__errorFound = False
        self.__tracksOrder = None
        self.__aOrder = []
        self.__translation = {}

    def __bool__(self):
        return not self.__errorFound

    def __getitem__(self, index):
        return self.__aOrder[index]

    def __iter__(self):
        return self

    def __next__(self):
        if self.__index >= len(self.__aOrder):
            self.__index = 0
            raise StopIteration
        else:
            self.__index += 1
            return self.__getitem__(self.__index - 1)

    def _split(self):
        if not (self.__tracksOrder.find(",") > 0) or not (self.__tracksOrder.find(":") > 0):
            self.__errorFound = True
        else:
            self.__aOrder = self.__tracksOrder.split(",")

    @property
    def aOrder(self):
        return self.__aOrder

    @property
    def order(self):
        return self.__tracksOrder

    @order.setter
    def order(self, value):
        self._initVars()
        self.__tracksOrder = value
        self._split()

    @property
    def translation(self):
        return self.__translation

    @translation.setter
    def translation(self, value):
        if isinstance(value, dict):
            self.__translation = value
            print("Proper Update.")

    def strOrder(self):

        strTmp = ""
        for track in self.aOrder:
            trk = self.translation.get(track, track)
            if not strTmp:
                strTmp += trk
            else:
                strTmp += "," + trk

        return strTmp

    def translationUpdate(self, value):
        if isinstance(value, dict):
            self.__translation.update(value)
