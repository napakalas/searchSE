from ..general import getUrlFromPmr, PMR_SERVER
from .pmrcollection import PmrCollection

class Categories(PmrCollection):
    def __init__(self, *paths):
        super().__init__(*paths)

    # get list of categories in the PMR
    def getListCategories(self, fromServer=False):
        if fromServer:
            return getUrlFromPmr(PMR_SERVER)[4:-3]
        else:
            return list(self.data.keys())
