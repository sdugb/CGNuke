
#coding=utf-8
import urllib
import urllib2
import cookielib
#from PySide import QtCore, QtGui
import json
import xml.dom.minidom
import time
import datetime
import re
import RCConfig_nuke
import hashlib
import streaminghttp
import encode
import zipfile
import shutil
import fnmatch
import os
import json
import nuke

monthInfo = {u'一月': 'January', u'二月': 'February', u'三月': 'March', u'四月':'April', 
                u'五月': 'May', u'六月': 'June', u'七月': 'July', u'八月': 'Aguest', 
                u'九月': 'September', u'十月': 'October', u'十一月': 'November', u'十二月': 'December'}

class DAMService():
 
    def __init__(self):
        self.url = RCConfig_nuke.myURL
        self.myDAMURL = RCConfig_nuke.myDAMURL

    def get(self, url, params):
        url1 = self.url + url     
        try:
            url1 = url1 + "?"
            for name in params:
                url1 = url1 + name + "=" + params[name] + "&"
            url2 = url1[0: len(url1) - 1]
            #print "url =", url2
            self.cookie = cookielib.CookieJar()
            req = urllib2.Request(url2)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
            response = opener.open(req)
            result = response.read()
            response.close()
            return result
        except urllib2.HTTPError, e:
            print e.code
            return False
        except urllib2.URLError, e:
            print e
            return False

    def post(self, url, params, method = None):
        url1 = self.url + url + '?'
        try:
            if method != None:
                url1 = 'method=' + method
            params_urlencode = urllib.urlencode(params)
            req = urllib2.Request(url1, params_urlencode)
            result_data = urllib2.urlopen(req)
            result = result_data.read()
            result_data.close()
            return result
        except urllib2.HTTPError, e:
            print e.code
            return False
        except urllib2.URLError, e:
            print e
            return False

    def send(self, url, params = ''):
        try:
            params_urlencode = urllib.urlencode(params)
            req = urllib2.Request(url, params_urlencode)
            result_data = urllib2.urlopen(req)
            result = result_data.read()
            result_data.close()
            return result
        except urllib2.HTTPError, e:
            print e.code
            return '0'
        except urllib2.URLError, e:
            print e
            return '1'        
    """
    def login(self, name, password, tl = 'true', hashed = 'false'):
        result  = self.send(self.myDAMURL + '/DAM/login',
                                {'name': name, 'pass': password, 'tl': tl, 'pass_hashed': hashed})
        self.myApiKey = result
        return result
    """
    def login(self, name, password):
        m = hashlib.md5()
        #m.update(password)
        m.update('gbzz01')
        psw = m.hexdigest()
        #self.service.login(user, psw.upper(), 'true', 'true')
        result  = self.send(self.myDAMURL + '/DAM/login', {'name': 'gb', 'pass': psw.upper(), 'tl': 'true', 'pass_hashed': 'true'})
        self.myApiKey = result
        nuke.error(self.myApiKey)

        result  = self.send(self.myDAMURL + '/RC/login', {'login': name, 'password': password})
        print 'result =', result
        return result

    def getuser(self):
        print 'apiKey =', self.myApiKey
        return self.send(self.myDAMURL + '/DAM/getUser', {'apiKey': self.myApiKey})
        
    def openscene(self, folderName):
        return self.send(self.myDAMURL + '/DAM/openScene',
                                 {'folderName': folderName, 'api_key': self.myApiKey})

    def submitjob(self, userName, jobName, projectName, sceneName, pluginName, frameList):
        return self.send(self.myDAMURL + '/rest/jobSubmit',
                                 {'user': userName, 'job': jobName, 'project': projectName, 'scene': sceneName, 
                                                'engine': pluginName, 'frameList': frameList})

    def getOuputDir(self, userName, jobName, projetcName, sceneName):
        return self.send(self.myDAMURL + '/rest/getOuputDir',
                                 {'user': userName, 'job': jobName, 'project': projectName, 'scene': sceneName})

    def makeOutputDir(self, userName, jobName, projectName, sceneName):
        return self.send(self.myDAMURL + '/rest/makeOutputDir',
                                 {'user': userName, 'job': jobName, 'project': projectName, 'scene': sceneName})

    def copyfiles(self, userName, jobName, projectName, sceneName, mayaPathList, texturePathList):
        return self.send(self.myDAMURL + '/DAM/copyFiles',
            {'userName': userName, 'jobName': jobName, 'project': projectName, 'sceneName': sceneName, 
                                                'mayaPathList': mayaPathList, 'texturePathList': texturePathList})

    def TBAuth(self):
        return self.send(self.myDAMURL + '/TB/auth')
    
    def TBGetUserInfo(self):
        return self.send(self.myDAMURL + '/TB/getUserInfo',
            {'appkey': RCConfig_maya.TBAppKey, 'secretkey': RCConfig_maya.TBSecretKey, 'code': RCConfig_maya.TBCode})
    """

    def TBGetUserInfo(self):
        return self.send(self.myDAMURL + '/TB/getUserInfo')
    """
    def myWFGetMyTask(self, user):
        return self.send(self.myDAMURL + '/myWF/getMyTasks', {'user': user})

    def myWFMyGetShotTask(self, user):
        return self.send(self.myDAMURL + '/myWF/getMyShotTasks', {'user': user})

    def myWFGetInvolvesTask(self, user):
        return self.send(self.myDAMURL + '/myWF/getMyInvolvesTasks', {'user': user})

    def myWFSubmitTask(self, task):
        #print 'task =', task
        return self.send(self.myDAMURL + '/myWF/submitTask', {'id': task['_id'], 'projectName': task['projectName']})

    def myWFReturnTask(self, taskName, projectName):
        return self.send(self.myDAMURL + '/DAM/returnTask', {'taskName': taskName, 'projectName': projectName})

    def myWFSetTaskAsset(self, taskName, projectName, Url, folderID):
        return self.send(self.myDAMURL + '/MyWF/setTaskAsset', {'taskName': taskName, 'projectName': projectName,
                                'IconUrl': Url, 'assetFolderID': folderID})


    def TBUpdateTaskStatus(self, task, status):
        return self.send(self.myDAMURL + '/TB/updateTaskStatus', {'taskID': task['_id'], 'status': status})

    def TBSubmitTask(self, taskID):
        return self.send(self.myDAMURL + '/TB/submitTask', {'taskID': taskID})

    def loginhost(self, name, password, hashed = '0'):
        url = '/global/api/authentication.cfc' 
        params = {'method': 'loginhost', 'name': name, 'pass': password, 'passhashed': hashed}
        return self.get(url, params)
    
    def getApiKey(self, name):
        result = self.send(self.myDAMURL + '/DAM/getApiKey', {'name': name})
        self.myApiKey = result
        return result

    def getfolders(self, folderid = '0', collectionfolder = 'false'):
        url = "/global/api2/folder.cfc"
        if folderid == '0':
            params = {'method': 'getfolders','api_key': self.myApiKey}
        else:
            params = {'method': 'getfolders','api_key': self.myApiKey, 'folderid': folderid,
                         'collectionfolder': collectionfolder}
        return self.get(url, params)

    def getallfolders(self, projectList):
        return self.send(self.myDAMURL + '/DAM/getAllFolders', {'projectIDList': projectList})  
    
    def getfolder(self, folderid, foldername):
        url = "/global/api2/folder.cfc"
        if folderid == '':          
            params = {'method': 'getfolder','api_key': self.myApiKey, 'foldername': foldername}
        elif foldername == '':
            params = {'method': 'getfolder','api_key': self.myApiKey, 'folderid': folderid}
        else:
            params = {'method': 'getfolder','api_key': self.myApiKey, 'folderid': folderid, 'foldername': foldername}
        return self.get(url, params)

    def getassets(self, folderid, show = 'all'):
        url = "/global/api2/folder.cfc"
        params = {'method': 'getassets', 'folderid': folderid, 'show': show, 'api_key': self.myApiKey}
        return self.get(url, params)   

    def getassets_last(self, folderid, show = 'all'):
        url = "/global/api2/folder.cfc"
        params = {'method': 'getassets', 'folderid': folderid, 'show': show, 'api_key': self.myApiKey}
        result = self.get(url, params)
        data = json.loads(result)

        array = []
        timeStamp1 = 0
        for arr in data['DATA']:
            if arr[0] == '1':
                return None
            l = arr[17]
            ll = l.split(',')
            lll = ll[0]
            #汉字
            if re.match('[ \u4e00 -\u9fa5]+', ll[0]) == None:
                mm = monthInfo[lll]
            else:
                mm = ll[0]
            if mm != None:
                str = mm + ', ' + ll[1]
            ti2 = time.strptime(str, "%B, %d %Y %H:%M:%S")
            timeStamp2 = int(time.mktime(ti2))
            if timeStamp2 > timeStamp1:
                array = arr
                timeStamp1 = timeStamp2
        fn = array[19]
        return fn

    def getasset(self, assetid, assettype):
        url = "/global/api2/asset.cfc"
        params = {'method': 'getasset', 'assetid': assetid, 'assettype': assettype, 'api_key': self.myApiKey}
        return self.get(url, params)

    def setfolder(self, folder_name, folder_related = '1', folder_colletcion = 'false'):
        url = "/global/api2/folder.cfc"
        if folder_related == '1':
            params = {'method': 'setfolder', 'folder_name': folder_name, 'api_key': self.myApiKey}
        else:
            params = {'method': 'setfolder', 'folder_name': folder_name, 'folder_colletcion': folder_colletcion,
                                     'folder_related': folder_related, 'api_key': self.myApiKey}
        return self.get(url, params)

    def removefolder(self, folder_id):
        url = "/global/api2/folder.cfc"
        params = {'method': 'removefolder', 'folder_id': folder_id, 'api_key': self.myApiKey}
        result = self.get(url, params)
        doc = xml.dom.minidom.parseString(result)
        status = doc.getElementsByTagName("ResponseCode")
        if status == '0':
            return True
        else:
            print doc.getElementsByTagName("message")
            return False

    def searchassets_ext(self, ext):
        url = "/global/api2/search.cfc"
        params = {'method': 'searchassets', 'api_key': self.myApiKey, 'searchfor': 'extension:(' + ext + ')'}
        return self.get(url, params)

    def adduser(self, username, password, email):
        url = "/global/api2/user.cfc"
        params = {'method': 'add', 'api_key': self.myApiKey, 'user_first_name': username,
                           'user_last_name': username, 'user_email': email,
                           'user_name': username, 'userpass': password, 'user_active': 'true'}
        return self.get(url, params)

    def gethosts(self):
        url = "/global/api2/hosts.cfc"
        params = {'method': 'gethosts', 'api_key': self.myApiKey}
        return self.get(url, params)

    def gethostsize(self, host_id):
        url = "/global/api2/hosts.cfc"
        params = {'method': 'gethostsize', 'host_id': host_id, 'api_key': self.myApiKey}
        return self.get(url, params)

    def setmetadata(self, assetid, assettype, assetmetadata):
        url = "/global/api2/asset.cfc"
        params = {'method': 'setmetadata', 'assetid': assetid, 'assettype': assettype,
                                     'assetmetadata': assetmetadata,'api_key': self.myApiKey}
        return self.get(url, params)

    def getmetadata(self, assetid, assettype, assetmetadata):
        url = "/global/api2/asset.cfc"
        params = {'method': 'getmetadata', 'assetid': assetid, 'assettype': assettype,
                                     'assetmetadata': assetmetadata,'api_key': self.myApiKey}
        return self.get(url, params)

    def upload(self, url, destfolderid, filedata, zip_extract = 'false'):
        handlers = [streaminghttp.StreamingHTTPHandler(), streaminghttp.StreamingHTTPRedirectHandler(),
                            urllib2.HTTPCookieProcessor(cookielib.CookieJar())]
        urllib2.install_opener(urllib2.build_opener(*handlers))
        datagen, headers = encode.multipart_encode({'fa': 'c.apiupload', 'destfolderid': destfolderid, 'zip_extract': zip_extract,
                            'api_key': self.myApiKey, "filedata": open(filedata, "rb")})
        request = urllib2.Request(self.url + url, datagen, headers)
        try:
            result = urllib2.urlopen(request).read()
            doc = xml.dom.minidom.parseString(result)
            #print doc.getElementsByTagName("responsecode")[0].firstChild.data
            if doc.getElementsByTagName("responsecode")[0].firstChild.data == '0':
                ret = {'status': '0', 'message': doc.getElementsByTagName("message")[0].firstChild.data, 
                                      'assetid': doc.getElementsByTagName("assetid")[0].firstChild.data,
                                      'filetype': doc.getElementsByTagName("filetype")[0].firstChild.data}
                return ret
            else:
                ret = {'status': '1', 'message': doc.getElementsByTagName("message")[0].firstChild.data}
                return ret
        except urllib2.HTTPError, e:
            ret = {'status': '2', 'message': 'HTTPError'}
            print e.code
            return ret
        except urllib2.URLError, e:
            ret = {'status': '3', 'message': 'URLError'}
            print 'url:', url
            print e
            return ret

    def userActionLog(self, user, projectName, sceneName, action):
        #count = RCConfig_maya.mouseCount
        count = 0
        #RCConfig_maya.mouseCount = 0
        return self.send(self.myDAMURL + '/rest/userActionLog', {'user': user, 
                            'projectName': projectName, 'sceneName': sceneName, 'action': action, 'mouseCount': count})

    def makefolder(self, upfolder_id, folder_name):
        result = self.getfolders(upfolder_id)
        data = json.loads(result)
        folder_id = None
        if data['DATA'] != []:
            for array in data['DATA']:
                if folder_name == array[1]:
                    folder_id = array[0]
                    break
        return folder_id

    def myDownload(self, url1, fileName, flag = True):
        if flag and os.path.isfile(fileName):
            return

        url = url1.replace('\\', '/')
        try:
            url_opener = urllib2.urlopen(url)
            #print url_opener
        except Exception,e:
            print 'open url error---1'
            print url
            print e
            return False
        if url_opener.code != 200:
            print 'return code is:%d'%(url_opener.code)
            return False
        if not url_opener.headers.has_key('Content-Length'):
            print 'no content length'
            return False
        content_length = long(url_opener.headers['Content-Length'])
        """
        gMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar');
        if RCConfig_maya.lang == 'zh':
            status = u'正在下载文件：' + url[url.rfind('/')+1:]
        else:
            status = u'download File：' + url[url.rfind('/')+1:]
        cmds.progressBar( gMainProgressBar,
                                    edit=True,
                                    beginProgress=True,
                                    isInterruptable=True,
                                    status=status
                                    )
        """
        download_size = 0
        target_file = open(fileName, 'wb')
        while download_size < content_length:
            try:
                str_content = url_opener.read(1024)
            except Exception,e:
                print 'read error:%s' % (str(e))
                return
            if not str_content or len(str_content)==0:
                print 'read error, connection close'
                return
            target_file.write(str_content)
            download_size += len(str_content)

            #cmds.progressBar(gMainProgressBar, edit=True, step=int(float(download_size)/float(content_length)*100.0))
        #cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
        print 'file has download: ', fileName
        return True

    def getUploadURL(self):
        """
        result = self.gethosts()
        data = json.loads(result)
        for array in data['DATA']:
            if array[0] == '1':
                return None
            if array[1] == 'Demo':
                hostPath = array[2]
                break
        url = '/' + hostPath + '/dam/index.cfm'
        """
        url = '/raz1/dam/index.cfm'
        return url

