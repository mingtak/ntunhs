from five import grok
from Products.Five.browser import BrowserView
from plone import api
from zope.interface import Interface


def removeItem(path):
    item = api.content.get(path=path)
    api.content.delete(obj=item)


class CleanTrashcan(BrowserView):
    def __call__(self):
        if not self.request.has_key('deletecheck'):
            return
        removeItems = self.request['deletecheck']
        if type(removeItems) == type(str()):
            removeItem(removeItems)
        else:
            for item in removeItems:
                removeItem(item)        
        trashcan = api.content.get(UID='559f90f72f3042b8ae23278c57e8e08b')
        return trashcan()


class IsAnonymous(grok.View):

    grok.context(Interface)

    def render(self):
        return api.user.is_anonymous()
