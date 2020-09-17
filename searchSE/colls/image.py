from .pmrcollection import PmrCollection

class Images(PmrCollection):
    def __init__(self, *paths):
        super().__init__(*paths)

    def getPath(self, id):
        return self.data[id]['path']

    def getTitle(self, id):
        return self.data[id]['title']
