from .general import *
from .pmrcollection import IrCollection

class Maths(IrCollection):
    def __init__(self, *paths):
        super().__init__(*paths)

    def add(self, text):
        mathId = self.getNewId()
        self.data[mathId] = text
        return mathId

    def getText(self, id):
        return self.data[id]
