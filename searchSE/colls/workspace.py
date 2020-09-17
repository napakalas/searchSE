from ..general import getUrlFromPmr, PMR_SERVER, CURRENT_PATH,WORKSPACE_DIR
from .pmrcollection import PmrCollection
import os

class Workspaces(PmrCollection):
    def __init__(self, *paths):
        super().__init__(*paths)
        self.allWksDir = os.path.join(CURRENT_PATH,WORKSPACE_DIR)
        self.statusC = {'deprecated': 0, 'current': 1, 'validating': 2}

    # get list of workspaces URL in the PMR
    def getListWorkspaces(self, fromServer=False):
        if fromServer:
            listWorkspaces = getUrlFromPmr(PMR_SERVER + 'workspace')
            tmp = [url[url.find('.org/') + 5:] for url in listWorkspaces]
            return tmp
        else:
            return list(self.data.keys())

    def getCellml(self, id=None, url=None):
        if id != None:
            url = self.getUrl(id)
        if url in self.data:
            if 'cellml' in self.data[url]:
                return self.data[url]['cellml']
        return []

    def getUrl(self, id):
        if id in self.id2Url:
            return self.id2Url[id]
        return None

    def getExposures(self, id=None, url=None):
        if id != None:
            url = self.getUrl(id)
        if url in self.data:
            if 'exposures' in self.data[url]:
                return self.data[url]['exposures']
        return {}
