from ..general import *
from .pmrcollection import PmrCollection

class Units(PmrCollection):
    def __init__(self, *paths):
        super().__init__(*paths)

    def add(self, elements):
        unitsN2Id = {}
        for element in elements:
            if element != None:
                name = element.attrib['name']
                unitText = ''
                for unit in element:
                    sortedUnit = {k: unit.attrib[k] for k in sorted(unit.attrib, reverse=True)}
                    unitText += ','.join([k + ':' + v for k,v in sortedUnit.items()]) + ';'
                if unitText in self.getT2Id():
                    id = self.getT2Id()[unitText]
                else:
                    id = self.getNewId()
                if id in self.data:
                    if name not in self.data[id]['names']:
                        self.data[id]['names'] += [name]
                else:
                    self.data[id] = {'names': [name], 'text': unitText}
                unitsN2Id[name] = id
        return unitsN2Id

    def addNewText(self, name, unitText):
        if unitText in self.getT2Id():
            id = self.getT2Id()[unitText]
        else:
            id = self.getNewId()
        if id in self.data:
            if name not in self.data[id]['names']:
                self.data[id]['names'] += [name]
        else:
            self.data[id] = {'names': [name], 'text': unitText}
        return id

    def getID(self, text):
        if text in self.getT2Id():
            return self.getT2Id()[text]
        else:
            return None

    def getText(self, id):
        if id in self.data:
            return self.data[id]['text']
        else:
            return None;

    def getNames(self, id=None, text=None):
        if id in self.data:
            return self.data[id]['names']
        elif text in self.getT2Id():
            return self.data[self.getT2Id()[text]]['names']
        else:
            return []

    def getId2T(self):
        return {v['text']:k for k,v in self.data.items()}

    def getT2Id(self):
        return {v['text']:k for k,v in self.data.items()}
