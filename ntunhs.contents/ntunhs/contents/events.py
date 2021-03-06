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

#自訂import
from plone import api
from zope.lifecycleevent.interfaces import IObjectAddedEvent, IObjectModifiedEvent, IObjectRemovedEvent
import os
import csv
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.Header import Header
from collective import dexteritytextindexer


#全域變數
#報名系統匯出目錄路徑
exportCsvDir = '/home/plone/Plone/zinstance/var/ntunhsExportCsv/'
#寄送csv檔執行路徑
sendCsvFileTo_path = '/home/plone/Plone/zinstance/var/ntunhsExportCsv/sendCsvFileTo.py'


# Interface class; used to define content-type schema.

class Ievents(form.Schema, IImageScaleTraversable):
    """
    events for NTUNHS
    """

    form.model("models/events.xml")
    #定義全文檢索欄位
    dexteritytextindexer.searchable('body')


class events(Container):
    grok.implements(Ievents)
    # Add your class methods and properties here

    #處理報名程序
    def sendApply(self):
        catalog = api.portal.get_tool(name='portal_catalog')
        applyContent = {'topic':str(self.REQUEST.form['topic']),
                        'name':str(self.REQUEST.form['name']),
                        'company_name':str(self.REQUEST.form['company_name']),
                        'your_title':str(self.REQUEST.form['your_title']),
                        'phone_number':str(self.REQUEST.form['phone_number']),
                        'phone_number2':str(self.REQUEST.form['phone_number2']),
                        'replyto':str(self.REQUEST.form['replyto']),
                        'certify_id':str(self.REQUEST.form['certify_id'])
                       }
        
        #catalog找uid
        objectId = str(self.REQUEST['BASE3']).split('/')[4]
        objectUid = str(catalog(id=objectId)[0]['UID'])

        #以csv格式寫入
        with open('%s%s%s' % (exportCsvDir, objectUid, '.csv'), 'ab') as fileName:
            csvFile = csv.writer(fileName, dialect='excel')
            csvFile.writerows([[applyContent['topic'],
                                applyContent['name'],
                                applyContent['company_name'],
                                applyContent['your_title'],
                                applyContent['phone_number'],
                                applyContent['phone_number2'],
                                applyContent['replyto'],
                                applyContent['certify_id']]])
        #寄出報名信件給承辦人
        foo = api.content.get(UID=objectUid)
        sendEmailTo = str(foo.sendEmailTo)

        msg = MIMEMultipart()
        msg['From'] = "cschu@ntunhs.edu.tw"
        msg['To'] = sendEmailTo
        msg['Subject'] = Header('%s%s%s' % ('健康照護產學營運中心:',
                                            applyContent['topic'],
                                            ' 有人報名'),
                                charset='UTF-8')
        mailBody = MIMEText('%s%s\n%s%s\n%s%s\n%s%s\n%s%s\n%s%s\n%s%s\n%s%s\n\n%s\n%s' % ( \
                             '活動名稱：', applyContent['topic'],
                             '姓名：', applyContent['name'],
                             '機構名稱：', applyContent['company_name'],
                             '職稱：', applyContent['your_title'],
                             '聯絡電話：', applyContent['phone_number'],
                             '聯絡電話2：', applyContent['phone_number2'],
                             'Email信箱：', applyContent['replyto'],
                             '公務人員ID：', applyContent['certify_id'],
                             '-----------------------------------------',
                             '本郵件由系統自動發出，請勿回覆本郵件'),
                            _subtype='plain',  _charset='UTF-8')
        msg.attach(mailBody)
        smtp = smtplib.SMTP()
        smtp.connect('smtp1.ntunhs.edu.tw:25')
        smtp.sendmail(msg['From'], msg['To'], msg.as_string())
        smtp.quit()
        return


#檢查ExpirationDate
def checkExpirationDate(object):
    if str(object.ExpirationDate()) == 'None':
        api.portal.show_message(message=u'您未設定報名截止日期! 請回上一頁設定。', type='error', request=object.REQUEST)
        raise ValueError('setup ExpirationDate not yet')


#event handle: 新增報名表
@grok.subscribe(Ievents, IObjectAddedEvent)
def notifyUser(object, event):
    checkExpirationDate(object)
    expirationDate = object.ExpirationDate()
    with open('%s%s%s' % (exportCsvDir, object.UID(), '.csv'), 'wb') as csvFileName:
        csvFile = csv.writer(csvFileName, dialect='excel')
        csvFile.writerows([['活動名稱', '姓名', '公司名稱', '職稱', '電話號碼', '電話號碼2', '電子郵件', '公務人員id']])

    #將script寫入uid+random.sh,再以at待命執行
    expirationDate = str(object.ExpirationDate())

    sendCsvDate = {'date':expirationDate.split('T')[0],
                   'hours':expirationDate.split('T')[1].split(':')[0],
                   'minutes':expirationDate.split('T')[1].split(':')[1]}
    script_content = '%s %s %s %s %s%s%s' % ('python',
                                             sendCsvFileTo_path,
                                             str(object.sendEmailTo),
                                             str(object.Title().replace(' ', '')),
                                             exportCsvDir, object.UID(), '.csv')
    shFileName = '%s%s%s%s' % (exportCsvDir, object.UID(), str(random.randint(100,999)), '.sh')
    with open(shFileName, 'w') as shFile:
        shFile.write(script_content)
    os.system('%s %s %s%s %s' % ('at -f', shFileName, sendCsvDate['hours'], sendCsvDate['minutes'], sendCsvDate['date']))


#event handle:修改報名表
@grok.subscribe(Ievents, IObjectModifiedEvent)
def notifyUser(object, event):
    checkExpirationDate(object)
    #刪掉舊script, at內容不用管
    os.system('%s%s%s%s' % ('rm ',exportCsvDir, object.UID(), '*.sh'))
    #將script寫入uid+random.sh,再以at待命執行
    expirationDate = str(object.ExpirationDate())

    sendCsvDate = {'date':expirationDate.split('T')[0],
                   'hours':expirationDate.split('T')[1].split(':')[0],
                   'minutes':expirationDate.split('T')[1].split(':')[1]}
    script_content = '%s %s %s %s %s%s%s' % ('python',
                                             sendCsvFileTo_path,
                                             str(object.sendEmailTo),
                                             str(object.Title().replace(' ', '')),
                                             exportCsvDir, object.UID(), '.csv')
    shFileName = '%s%s%s%s' % (exportCsvDir, object.UID(), str(random.randint(100,999)), '.sh')
    with open(shFileName, 'w') as shFile:
        shFile.write(script_content)
    os.system('%s %s %s%s %s' % ('at -f', shFileName, sendCsvDate['hours'], sendCsvDate['minutes'], sendCsvDate['date']))


#event handle:刪除報名表
@grok.subscribe(Ievents, IObjectRemovedEvent)
def notifyUser(object, event):
    os.system('%s%s%s%s' % ('rm ',exportCsvDir, object.UID(), '*'))


class SampleView(grok.View):
    """ sample view class """

    grok.context(Ievents)
    grok.require('zope2.View')

    grok.name('view')

    # Add view methods here
