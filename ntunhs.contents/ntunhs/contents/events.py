# -*- coding: utf-8 -*-
from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.dexterity.content import Container
from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable


from ntunhs.contents import MessageFactory as _
from plone import api
from zope.lifecycleevent.interfaces import IObjectAddedEvent, IObjectModifiedEvent

#全文檢索用
from collective import dexteritytextindexer


# Interface class; used to define content-type schema.

class Ievents(form.Schema, IImageScaleTraversable):
    """
    events for NTUNHS
    """

    # If you want a schema-defined interface, delete the model.load
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/events.xml to define the content type.

    form.model("models/events.xml")
    #定義全文檢索欄位
    dexteritytextindexer.searchable('body')

# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.


class events(Container):
    grok.implements(Ievents)
    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# events_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

#測試發生,這段隨時可刪除
'''
def writein(string=str()):
    with open('/home/plone/ntunhsyyyyy', 'a') as foo:
        foo.write(string + '\n')
'''

#報名系統匯出目錄路徑
exportCsvDir = '/home/plone/Plone/zinstance/var/ntunhsExportCsv/'

#檢查ExpirationDate
def checkExpirationDate(object):
    if str(object.ExpirationDate()) == 'None':
        api.portal.show_message(message=u'您未設定報名截止日期! 請回上一頁設定。', type='error', request=object.REQUEST)
        raise ValueError('setup ExpirationDate not yet')

#event handle: 新增報名表
@grok.subscribe(Ievents, IObjectAddedEvent)
def notifyUser(object, event):
    checkExpirationDate(object)
    with open('%s%s%s' % (exportCsvDir, object.UID(), '.date'), 'w') as exportCsv:
        exportCsv.write(str(object.ExpirationDate()))

#event handle:修改報名表
@grok.subscribe(Ievents, IObjectModifiedEvent)
def notifyUser(object, event):
    checkExpirationDate(object)
    with open('%s%s%s' % (exportCsvDir, object.UID(), '.date'), 'w') as exportCsv:
        exportCsv.write(str(object.ExpirationDate()))


class SampleView(grok.View):
    """ sample view class """

    grok.context(Ievents)
    grok.require('zope2.View')

    grok.name('view')

    # Add view methods here
