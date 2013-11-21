# -*- coding: utf-8 -*-
from plone import api


def getTitle(self):
    virtualPath = str(self.REQUEST['VIRTUAL_URL_PARTS'][-1])
    content = api.content.get(path='ntunhs/' + virtualPath)
    #判斷編碼
    try:
        if isinstance(content.title, unicode):
            title = content.title.encode('utf-8')
        else:
            title = content.title
    except:
        title = None
    return title
