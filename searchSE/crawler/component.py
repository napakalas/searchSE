from ..general import *
from .pmrcollection import PmrCollection

class Components(PmrCollection):
    def __init__(self, *paths):
        super().__init__(*paths)

    def add(self, cellmlId, varString, compsT2Id):
        """Adding a new component, returning compId and list of new component"""
        varParts = varString.split('/')
        compName = varParts[0] if len(varParts) == 1 else varParts[-2] if varParts[-1] != 'prime' else varParts[-3]
        if len(varParts) >= 2: # consisted of component and variable names
            # identify component and encapsulation
            compRange = len(varParts) - 1 if varParts[-1] != 'prime' else len(varParts) - 2
            for i in range(compRange):
                if varParts[i] not in compsT2Id:
                    compId = self.getNewId()
                    compsT2Id[varParts[i]] = compId
                    self.data[compId] = {'name': varParts[i], 'cellml': cellmlId}
                else:
                    compId = compsT2Id[varParts[i]]
                if i > 0:
                    self.data[compId]['parent'] = varParts[i - 1]
            # identify children
            for i in range(compRange - 1):
                compId = compsT2Id[varParts[i]]
                if 'children' in self.data[compId]:
                    if compsT2Id[varParts[i + 1]] not in self.data[compId]['children']:
                        self.data[compId]['children'] += [compsT2Id[varParts[i + 1]]]
                else:
                    self.data[compId]['children'] = [compsT2Id[varParts[i + 1]]]
        else:
            return None
        compId = compsT2Id[compName]
        return compId

    def addVariable(self, compId, varId):
        if 'variables' in self.data[compId]:
            self.data[compId]['variables'] += [varId]
        else:
            self.data[compId]['variables'] = [varId]

    def getT2Id(self, ids=None):
        if isinstance(ids,list):
            return {self.data[id]['name']:id for id in ids}
        return {}
        # return {v['name']:k for k,v in self.data.items()}

    def setVarRef(self, compId, varId, varName):
        if 'varRefs' not in self.data[compId]:
            self.data[compId]['varRefs'] = {}
        self.data[compId]['varRefs'][varId] = varName

    def setCellml(self, compId, cellmlId):
        self.data[compId]['cellml'] = cellmlId

    def getVariables(self, compId):
        if 'variables' in self.data[compId]:
            return self.data[compId]['variables']
        else:
            # some components such as parent components may not have variables
            # but they have children components which may have variable
            return []

    def getName(self,compId):
        return self.data[compId]['name']

    def getCellml(self, id):
        return self.data[id]['cellml']
