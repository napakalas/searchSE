from ..general import getUrlFromPmr, PMR_SERVER
from .pmrcollection import PmrCollection

class Exposures(PmrCollection):
    def __init__(self, workspaces, *paths):
        super().__init__(*paths)
        self.workspaces = workspaces
        self.wksData = workspaces.getJson()['data']
        self.statusC = {'deprecated': 0, 'current': 1, 'validating': 2}

    def getListExposures(self, fromServer=False):
        if fromServer:
            listExposure = getUrlFromPmr(PMR_SERVER + 'exposure')
            tmp = [url[url.find('.org/') + 5:] for url in listExposure]
            return tmp
        else:
            return list(self.data.keys())
