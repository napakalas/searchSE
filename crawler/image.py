from .general import *
from .pmrcollection import IrCollection

class Images(IrCollection):
    def __init__(self, *paths):
        super().__init__(*paths)

    def add(self, elements, cellmlId):
        ids = []
        for figure in elements:
            ns = '{'+figure.nsmap[None] +'}'
            figId = figure.attrib['id'] if 'id' in figure.attrib else ''
            caption = figure.find('.//' + ns + 'caption')
            figCaption = caption.text if caption != None else ''
            title = figure.find('.//' + ns + 'title')
            figTitle = title.text if title != None else ''
            figFile = figure.find('.//' + ns + 'imagedata').attrib['fileref']
            id = self.getNewId()
            self.data[id] = {'name':figId, 'caption':figCaption,'title':figTitle,'path':figFile,'celml':cellmlId}
            ids += [id]
        return ids
