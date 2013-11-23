# -*- coding: utf-8 -*-
from plone import api


#活動報名表取出活動名稱
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


#取出頂部導航
def getTopNav(self):
    catalog = api.portal.get_tool(name='portal_catalog')
    items = catalog(portal_type='Folder')
    result = str()
    for item in items:
        if not item.exclude_from_nav:
            result += "%s\t%s\n" % (item.Title, item.getPath())
    return result
