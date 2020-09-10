from ..general import *
from .pmrcollection import PmrCollection

class Variables(PmrCollection):
    def __init__(self, sysMaths, *paths):
        super().__init__(*paths)
        self.sysMaths = sysMaths

    def add(self, varId, varValue, name, compId, varType):
        varParts = name.split('/')
        shortName = varParts[-1] if varParts[-1] != 'prime' else varParts[-2]
        self.data[varId] = {'init': varValue, 'name': name, 'shortName': shortName, 'component': compId, 'type': varType}

    def addElement(self, elements):
        variablesT2Id = {}
        for element in elements:
            varName = element.attrib['name']
            if varName in varsT2Id:
                varId = varsT2Id[varName]
                varUnit = element.attrib['units']
                unitId = unitsN2Id[varUnit] if varUnit in unitsN2Id else varUnit
                self.data[varId]['unit'] = unitId
            else:
                varId = mapVars[varName]
            if self.data[varId]['component'] != compId:
                if 'varRefs' not in self.sysComps[compId]:
                    self.sysComps[compId]['varRefs'] = {}
                self.components[compId]['varRefs'][varId] = varName
            self.__setMetaFromElement(element, modelMeta, varId)

    def getT2Id(self, ids=None, short=False):
        if ids != None:
            return {self.getName(id, short):id for id in ids if self.getType(id) != 'rate'}
        return {self.getName(id, short):id for id in self.data if self.getType(id) != 'rate'}

    def getName(self, id, short=False):
        if short:
            return(self.data[id]['shortName'])
        return(self.data[id]['name'])

    # def getId(self, compId, varName):
    #     pass

    def getType(self, id):
        return self.data[id]['type']

    def getInit(self, id):
        return self.data[id]['init']

    def getRate(self, id):
        if self.getType(id) == 'state':
            return self.data[id]['rate']
        return None

    def setUnit(self, id, unitId):
        if unitId != None:
            self.data[id]['unit'] = unitId

    def addDependents(self, id, varDepId, mathVar):
        if 'dependent' not in self.data[id]:
            self.data[id]['dependent'] = {}
        if varDepId in self.data:
            self.data[id]['dependent'][varDepId] = mathVar

    def setMap(self, id, varMapId):
        self.data[id]['map'] = varMapId

    def addMath(self, id, mathText):
        if 'math' in self.data[id]:
            listText = [self.sysMaths.getText(mathId) for mathId in self.data[id]['math']]
            if mathText not in listText:
                mathId = self.sysMaths.add(mathText)
                self.data[id]['math'] += [mathId]
        else:
            mathId = self.sysMaths.add(mathText)
            self.data[id]['math'] = [mathId]

    def getMaths(self, id):
        varMaths = {}
        if 'math' in self.data[id]:
            for mathId in self.data[id]['math']:
                varMaths[mathId] = self.sysMaths.getText(mathId)
        return varMaths

    def getDependents(self, id, varDep={}):
        if 'dependent' in self.data[id]:
            if len(self.data[id]['dependent']) > 0:
                for varIdDep, varNameDep in self.data[id]['dependent'].items():
                    if varIdDep not in varDep:
                        varDep[varIdDep]={'name':varNameDep, 'math':self.getMaths(varIdDep), 'type':self.getType(varIdDep), 'init':self.getInit(varIdDep)}
                        if 'dependent' in self.data[varIdDep]:
                            if len(self.data[varIdDep]['dependent']) > 0:
                                self.getDependents(varIdDep, varDep)

    def getUnit(self, id):
        return self.data[id]['unit']

    def getPlots(self, id):
        if 'plot' in self.data[id]:
            return self.data[id]['plot']
        return []

    def getCompId(self, id):
        return self.data[id]['component']

    def addPlot(self, id, plotId):
        if 'plot' in self.data[id]:
            if plotId not in self.data[id]['plot']:
                self.data[id]['plot'] += [plotId]
        else:
            self.data[id]['plot'] = [plotId]

    def setRate(self, id, rate):
        self.data[id]['rate'] = rate
