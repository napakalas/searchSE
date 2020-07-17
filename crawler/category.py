from .general import *
from .pmrcollection import IrCollection

class Categories(IrCollection):
    def __init__(self, *paths):
        super().__init__(*paths)

    # get list of categories in the PMR
    def getListCategories(self, fromServer=False):
        if fromServer:
            return getUrlFromPmr(pmr_server)[4:-3]
        else:
            return list(self.data.keys())

    # update local categories
    def update(self):
        views = Views('resources', 'listOfView.json')
        # get of update categories
        listCategories = self.getListCategories(fromServer=True)
        print(len(listCategories))
        counter = 0
        print('updating %d categories ...'%len(listCategories))
        for category in listCategories:
            print(counter,end=' ')
            counter+=1
            listViews = getJsonFromPmr(category)
            txtCat = category[category.rfind('/') + 1:]
            self.data[txtCat] = []  # listViews['links']
            for view in listViews['links']:
                txtView = view['href'][len(pmr_server):]
                prompt = view['prompt']
                rel = view['rel']
                self.data[txtCat] += [txtView]
                views.add(txtView, prompt, rel, txtCat)
        # save list of categories file
        self.dumpJson()
        # save list of views file
        views.dumpJson()

    def extract(self):

        self.dumpJson()
