#coding=utf-8
import os
import shutil
import nuke
from nukescripts import panels
import json
import zipfile
import CGConfig_nuke

if nuke.env["gui"]:
    def loginWindow(service):
        CGConfig_nuke.service = service
        panel = nuke.Panel('登录账号')
        result, message = service.myWFGetAllTeams()
        print 'result =', result
        if not result:
            nuke.message(message)
            return
        CGConfig_nuke.teamList = message
        str = ' '
        for team in CGConfig_nuke.teamList:
            str = str + ' ' + team['alias']
        panel.addEnumerationPulldown('团队', str)
        panel.addSingleLineInput('账号', CGConfig_nuke.userName)
        panel.addPasswordInput('密码', CGConfig_nuke.password)
        #panel.addSingleLineInput('account', 'ssm')
        #panel.addPasswordInput('password', 'ssm1234')
        #panel.addEnumerationPulldown('选择类型', 'Single Sequence')

        panel.addButton('取消')
        panel.addButton('登录')
        panel.setWidth(300)
        ret = panel.show()
        if ret == 1:
            nuke.tprint(panel.value('账号'))
            nuke.tprint(type(panel.value('账号')))
            result, message = CGConfig_nuke.service.login(panel.value('账号'), panel.value('密码'))
            if result:
                CGConfig_nuke.userName = panel.value('账号')
                CGConfig_nuke.password = panel.value('密码')
                CGConfig_nuke.service.userActionLog(CGConfig_nuke.userName, '', '', 'loginNuke')
                return True
            else:
                nuke.message(message)
                return False
        else:
            return False

    def openWindow(renderType):
        panel = nuke.Panel('我的任务')
        result = CGConfig_nuke.service.getRenderJobInfo(CGConfig_nuke.userName, renderType)
        CGConfig_nuke.tasks = json.loads(result)
        #nuke.tprint(CGConfig_nuke.tasks)
        if not CGConfig_nuke.tasks:
            nuke.message('当前没有任务！！！')
            return
        #nuke.tprint(CGConfig_nuke.tasks)
        panel.addSingleLineInput('项目', CGConfig_nuke.tasks[0]['projectName'])
        str = ''
        for task in CGConfig_nuke.tasks:
            str = str + ' ' + task['name']
        panel.addEnumerationPulldown('Task', str)
        fileTypeList = 'tiff ' + 'dpx ' + 'exr ' + 'fpi ' + 'hdr ' + 'jpeg ' + 'mov ' + 'null ' + 'pic ' + 'png ' + 'sgi ' + 'taga ' + 'cin ' +'xpm ' + 'yuv'
        panel.addEnumerationPulldown('OutputFileType', fileTypeList)
        panel.addButton('刷新')
        panel.addButton('打开')
        panel.addButton('取消')

        panel.setWidth(400)
        ret = panel.show()
        if ret == 1: #打开
            nuke.scriptClear()
            CGConfig_nuke.taskName = panel.value('Task')
            CGConfig_nuke.renderType = renderType
            CGConfig_nuke.fileType = panel.value('OutputFileType')
            CGConfig_nuke.currentRenderTask = None
            openShotFile(renderType)
            menubar = nuke.menu('Nuke')
            menubar.findItem('RCMenu/保存任务').setEnabled(True)
            menubar.findItem('RCMenu/提交渲染').setEnabled(True)
            menubar.findItem('RCMenu/退回任务').setEnabled(True)
            return False
        elif ret == 2: #取消
            return False
        elif ret == 0: #刷新
            readNodeList = [r for r in RecursiveFindNodes('Read', nuke.root())]
            for readNode in readNodeList:
                #nuke.tprint(readNode)
                path = readNode['file'].value()
                nuke.error(path)
            return True
        nuke.scriptOpen(CGConfig_nuke.scriptFile)
        menubar = nuke.menu('Nuke')
        menubar.findItem('RCMenu/保存任务').setEnabled(True)
        if renderType == 'Single':
            menubar.findItem('RCMenu/提交渲染').setEnabled(True)
        else:
            menubar.findItem('RCMenu/提交渲染').setEnabled(False)
        menubar.findItem('RCMenu/退回任务').setEnabled(True)

    def openShotFile(renderType):
        for task in CGConfig_nuke.tasks:
            if CGConfig_nuke.taskName == task['name']:
                CGConfig_nuke.currentRenderTask = task
                projectName = task['projectName']
                break
        #nuke.tprint(CGConfig_nuke.currentRenderTask)
        parentProject = CGConfig_nuke.service.myWFGetParentProjectInfo(projectName)
        CGConfig_nuke.service.setRazunaURL(parentProject['DBHost'], parentProject['DBPort'], parentProject['appKey'])
        if CGConfig_nuke.currentRenderTask:
            CGConfig_nuke.projectName = CGConfig_nuke.currentRenderTask['projectName']
        else:
            nuke.error('CGConfig_nuke.currentRenderTask is error')
            return
        CGConfig_nuke.taskName = CGConfig_nuke.currentRenderTask['name']

        projectDir = CGConfig_nuke.storageDir + '/' + projectName
        if not os.path.exists(projectDir):
            os.mkdir(projectDir)
        taskDir = projectDir + '/' + CGConfig_nuke.taskName
        if not os.path.exists(taskDir):
            os.mkdir(taskDir)
        CGConfig_nuke.shotDir = taskDir
        singleSequenceDir = taskDir + '/' + CGConfig_nuke.renderType
        if not os.path.exists(singleSequenceDir):
            os.mkdir(singleSequenceDir)
        CGConfig_nuke.service.getShotZipFileList(CGConfig_nuke.currentRenderTask['taskID'],
                                                 CGConfig_nuke.currentRenderTask['outputDir1'],
                                                 CGConfig_nuke.currentRenderTask['renderType'])
        list = CGConfig_nuke.service.myWFGetTaskInfo(CGConfig_nuke.currentRenderTask['taskID'])
        CGConfig_nuke.currentRenderTask = list[0]
        # nuke.tprint(CGConfig_nuke.currentRenderTask)
        #nuke.tprint(renderType)
        if renderType == 'Single':
            shotFolderID = CGConfig_nuke.currentRenderTask['shotSingleFolderID']
        else:
            shotFolderID = CGConfig_nuke.currentRenderTask['shotSequenceFolderID']
        #nuke.tprint(shotFolderID)
        logJsonData = []
        logFilePath = singleSequenceDir + '/' + CGConfig_nuke.taskName + CGConfig_nuke.logFileExt
        if os.path.isfile(logFilePath):
            with open(logFilePath, "r") as json_file:
                logJsonData = json.load(json_file)
        bFlag = False
        assetList = CGConfig_nuke.service.getassets_last_all(shotFolderID)
        for asset in assetList:
            #nuke.tprint(asset['fileName'])
            name = asset['fileName'].split('.')[0]
            dir1 = singleSequenceDir + '/' + name
            if not os.path.exists(dir1):
                os.mkdir(dir1)
            shotFileName = dir1 + '/' + asset['fileName']
            #nuke.tprint(shotFileName)
            bExist = judgelogData(logJsonData, asset['fileName'], asset['ID'])
            if bExist != 2:
                nuke.tprint(shotFileName)
                CGConfig_nuke.service.myDownload(asset['URL'], shotFileName, False)
                zf = zipfile.ZipFile(shotFileName, 'r', zipfile.ZIP_DEFLATED, allowZip64=True)
                zf.extractall(dir1)
                zf.close()
                # os.remove(shotFileName)
                if bExist == 0:
                    logJsonData.append({"fileName": asset['fileName'], 'id': asset['ID']})
                bFlag = True
        if bFlag:
            with open(logFilePath, "w") as json_file:
                json.dump(logJsonData, json_file)

        nukeScriptFile = ''
        try:
            scriptFolderID = CGConfig_nuke.currentRenderTask['scriptFolderID']
        except KeyError:
            scriptFolderID = ''
        #nuke.tprint(scriptFolderID)
        if scriptFolderID:
            scriptList = CGConfig_nuke.service.getassets_last_all(scriptFolderID)
            for script in scriptList:
                nuke.tprint(script)
                name = script['fileName'].split('.')[0]
                type = name.split('_').pop()
                if type == CGConfig_nuke.renderType:
                    nukeScriptFile = script['fileName']
                    scriptFileURL = script['URL']
                    break
        CGConfig_nuke.readNodeList = []
        if not nukeScriptFile:
            shotDirList = os.listdir(singleSequenceDir)
            for shotDir in shotDirList:
                if os.path.isfile(singleSequenceDir + '/' + shotDir):
                    continue
                dir2 = singleSequenceDir + '/' + shotDir
                shotFileList = os.listdir(dir2)
                if renderType == 'Single':
                    for shotFile in shotFileList:
                        if shotFile.split('.')[1] == 'zip':
                            continue
                        node = nuke.createNode('Read')
                        shotPath = dir2 + '/' + shotFile
                        node['file'].fromUserText(shotPath)
                        CGConfig_nuke.readNodeList.append(node)
                else:
                    for shotFile in shotFileList:
                        ext = shotFile.split('.').pop()
                        name = shotFile.split('.')[0]
                        if not ext == 'zip':
                            break
                    dFile = dir2 + '/' + name + '.####.' + ext
                    nuke.error(dFile)
                    strList = []
                    n = 0
                    for shotFile in shotFileList:
                        if shotFile.split('.').pop() == 'zip':
                            continue
                        strList.append(shotFile.split('.')[1])
                        n = n + 1
                    strList.sort()
                    node = nuke.createNode('Read')
                    frameStr = strList[0] + '-' + strList[n - 1]
                    nuke.tprint(frameStr)
                    node['file'].fromUserText(dFile + ' ' + frameStr)
                    CGConfig_nuke.readNodeList.append(node)
        else:
            CGConfig_nuke.scriptFile = taskDir + '/' + nukeScriptFile
            nuke.tprint('NK file is Downloading...')
            CGConfig_nuke.service.myDownload(scriptFileURL, CGConfig_nuke.scriptFile, False)
            nuke.scriptOpen(CGConfig_nuke.scriptFile)
            rNodeList = [r for r in RecursiveFindNodes('Read', nuke.root())]
            for readNode in rNodeList:
                path = readNode['file'].value()
                dir = os.path.dirname(path)
                fname = os.path.basename(path)
                #nuke.tprint(dir)
                nodeName = os.path.basename(dir)
                path = singleSequenceDir + '/' + nodeName + '/' + fname
                readNode["file"].setValue(path)
                CGConfig_nuke.readNodeList.append(readNode)

        CGConfig_nuke.service.userActionLog(CGConfig_nuke.userName, CGConfig_nuke.projectName,
                                            CGConfig_nuke.taskName,
                                            'OpenNuke_' + CGConfig_nuke.renderType)

    def judgelogData(logJsonData, fileName, id):
        bExist = 0
        for log in logJsonData:
            if log['fileName'] == fileName and log['id'] == id:
                bExist = 2
                break
            elif log['fileName'] == fileName and log['id'] != id:
                log['id'] = id
                bExist = 1
                break
        return bExist

    def saveWindow():
        if CGConfig_nuke.projectName == '':
            nuke.error("没有当前任务")
        projectDir = CGConfig_nuke.storageDir + '/' + CGConfig_nuke.projectName
        taskDir = projectDir +'/' + CGConfig_nuke.taskName
        CGConfig_nuke.shotDir = taskDir
        singleSequenceDir = taskDir + '/' + CGConfig_nuke.renderType
        url = CGConfig_nuke.service.getUploadURL()
        otherDir = singleSequenceDir + '/' + 'otherDir'
        if not os.path.exists(otherDir):
            os.mkdir(otherDir)
        zipFileName = otherDir + '/' + 'otherDir.zip'
        zf = zipfile.ZipFile(zipFileName, "w", zipfile.ZIP_STORED, allowZip64=True)
        readNodeList = [r for r in RecursiveFindNodes('Read', nuke.root())]
        for readNode in readNodeList:
            path = readNode['file'].value()
            if readNode in CGConfig_nuke.readNodeList:
                #nuke.tprint(readNode)
                continue
            fn = os.path.basename(path)
            otherFile = otherDir + '/' + fn
            nuke.tprint(path)
            nuke.tprint(otherFile)
            shutil.copyfile(path, otherFile)
            zf.write(otherFile, fn)
            readNode["file"].setValue(otherFile)
        zf.close()
        CGConfig_nuke.service.upload(url, CGConfig_nuke.currentRenderTask['shotSingleFolderID'], zipFileName)
        if CGConfig_nuke.renderType == 'Single':
            CGConfig_nuke.scriptFile = taskDir + '/' + CGConfig_nuke.taskName + '_Single.nk'
        else:
            CGConfig_nuke.scriptFile = taskDir + '/' + CGConfig_nuke.taskName + '_Sequence.nk'
        try:
            scriptFolderID = CGConfig_nuke.currentRenderTask['scriptFolderID']
        except KeyError:
            scriptFolderID = CGConfig_nuke.service.makefolder(CGConfig_nuke.currentRenderTask['assetFolderID'],
                                                  CGConfig_nuke.razuna_Script_Dir)
            if not scriptFolderID:
                scriptFolderID = CGConfig_nuke.service.setfolder(CGConfig_nuke.razuna_Script_Dir,
                                                     CGConfig_nuke.currentRenderTask['assetFolderID'])

        nuke.scriptSaveAs(filename = CGConfig_nuke.scriptFile, overwrite = 1)
        ret = CGConfig_nuke.service.upload(url, scriptFolderID, CGConfig_nuke.scriptFile)
        nuke.tprint(CGConfig_nuke.currentRenderTask['_id'])
        CGConfig_nuke.service.setScriptFolderID(CGConfig_nuke.currentRenderTask['_id'], scriptFolderID)
        CGConfig_nuke.service.userActionLog(CGConfig_nuke.userName, CGConfig_nuke.projectName,
                                            CGConfig_nuke.taskName, 'SaveNuke')
        nuke.scriptClear()

    def createGraph():
        readNodeList = [r for r in RecursiveFindNodes('Read', nuke.root())]
        for readNode in readNodeList:
            path = readNode['file'].value()
            nuke.error(path)
        r1 = findReadNode(readNodeList, 'bg_cl_direct_diffuse')
        r2 = findReadNode(readNodeList, 'bg_cl_indirect_diffuse')
        r3 = findReadNode(readNodeList, 'bg_cl_emission')
        if r1 and r2 and r3:
            m1 = nuke.nodes.Merge(inputs = [r1, r2, r3])

        r4 = findReadNode(readNodeList, 'bg_cl_direct_specular')
        r5 = findReadNode(readNodeList, 'bg_cl_reflection')
        if r4 and r5:
            m2 = nuke.nodes.Merge(inputs=[r4, r5])

        m3 = nuke.nodes.Merge(inputs=[m1, m2])

        r6 = findReadNode(readNodeList, 'bg_cl_indirect_specular')
        m4 = nuke.nodes.Merge(inputs=[m3, r6])

    def findReadNode(readNodeList, name):
        node = None
        for readNode in readNodeList:
            path = readNode['file'].value()
            fn = os.path.basename(path)
            if name == fn.split('.')[0]:
                node  = readNode
                break
        return node

    def RecursiveFindNodes(nodeClass, startNode):
        if startNode.Class() == nodeClass:
            yield startNode
        elif isinstance(startNode, nuke.Group):
            for child in startNode.nodes():
                for foundNode in RecursiveFindNodes(nodeClass, child):
                    yield foundNode

    def executeWindow():
        outputPath = os.path.join(CGConfig_nuke.shotDir, 'output')
        if not os.path.isdir(outputPath):
            os.mkdir(outputPath)
        """
        writeNodeList = [r for r in RecursiveFindNodes('Write', nuke.root())]
        writeNode  = None
        for writeNode in writeNodeList:
            path = writeNode['file'].value()
            nuke.error(path) # f:/nuke/HFNL/HFNL_S01C124/output/HFNL_S01C124.%04d.tiff
        """
        node = nuke.createNode('Write')
        nuke.tprint(CGConfig_nuke.fileType)
        dFile = os.path.join(outputPath, CGConfig_nuke.taskName + '.%04d.' + CGConfig_nuke.fileType)
        sFrame = nuke.root().firstFrame()
        eFrame = nuke.root().lastFrame()
        frameList = str(sFrame) + '-' + str(eFrame)
        ret = nuke.getFramesAndViews('输入帧数', frameList)
        nuke.tprint(ret[0])
        node['file'].fromUserText(dFile + ' ' + ret[0])
        sFrame = int(ret[0].split('-')[0])
        eFrame = int(ret[0].split('-')[1])
        nuke.tprint(sFrame)
        nuke.tprint(eFrame)
        if eFrame < sFrame:
            return
        nuke.execute(node, sFrame, eFrame, 1)
        CGConfig_nuke.service.userActionLog(CGConfig_nuke.userName, CGConfig_nuke.projectName,
                                            CGConfig_nuke.taskName, 'ExecuteNuke')

    def outputFile():
        nuke.error('outputFile')
        outputPath = os.path.join(CGConfig_nuke.shotDir, 'output')
        zipFN = os.path.join(outputPath, CGConfig_nuke.taskName + '.zip')
        zipFP = zipfile.ZipFile(zipFN, 'w', zipfile.ZIP_DEFLATED)
        fileList = os.listdir(outputPath)
        nuke.tprint('fileList =', fileList)
        for file in fileList:
            filePath = os.path.join(outputPath, file)
            if not os.path.isfile(filePath):
                continue
            if file.split('.').pop() == 'zip':
                continue
            zipFP.write(filePath, file)
        zipFP.close()
        url = CGConfig_nuke.service.getUploadURL()
        folderID = CGConfig_nuke.currentTask['assetFolderID']
        resultFolderID = CGConfig_nuke.service.makefolder(folderID, CGConfig_nuke.razuna_Result_Dir)
        if not resultFolderID:
            resultFolderID = CGConfig_nuke.service.setfolder(CGConfig_nuke.razuna_Result_Dir, folderID)
        CGConfig_nuke.service.upload(url, resultFolderID, zipFN)

    def submitWindow():
        if CGConfig_nuke.renderType == 'Sequence':
            return
        #saveWindow()
        mapList = []

        panel = nuke.Panel('提交渲染')
        panel.addSingleLineInput('作业名', '')
        panel.addSingleLineInput('项目名', CGConfig_nuke.projectName)
        panel.addSingleLineInput('镜头名', CGConfig_nuke.taskName)

        str = '序列渲染并合成 序列渲染'
        panel.addEnumerationPulldown('渲染方式', str)
        panel.addButton('取消')
        panel.addButton('提交')
        panel.setWidth(300)
        ret = panel.show()
        if ret == 1:
            jobName = panel.value('作业名')
            nuke.tprint(jobName)
            """
            readNodeList = [r for r in RecursiveFindNodes('Read', nuke.root())]
            for readNode in readNodeList:
                path = readNode['file'].value()
                nuke.error(path)
                if path.find('otherDir') >= 0:
                    if os.path.isfile(path):
                       panel = nuke.Panel('图片与序列对应表')
                       dir = path.split('Single')[0]
                       panel.addFilenameSearch(path + '--->', dir)
                       panel.addButton('确认')
                       panel.addButton('取消')
                       ret = panel.show()
                       if ret == 0:
                           mapList.append(
                               {'single': os.path.basename(path), 'Sequence': panel.value(path + '--->')})
            
            """
            destFile = CGConfig_nuke.scriptFile.replace('_Single.nk', '_Sequence.nk')
            #nuke.tprint(CGConfig_nuke.currentRenderTask)
            taskList = CGConfig_nuke.service.myWFGetTaskInfo(CGConfig_nuke.currentRenderTask['_id'])
            task = taskList[0]
            #nuke.error(task[0]['frameList'])
            processNukeFile(CGConfig_nuke.scriptFile, destFile, mapList, task['frameList'])
            """
            lightTask = CGConfig_nuke.service.myWFsearchTaskByStage(CGConfig_nuke.taskName, CGConfig_nuke.projectName,
                                                                    '灯光')
            CGConfig_nuke.service.myWFSubmitTask(lightTask[0]['_id'], CGConfig_nuke.projectName)
            CGConfig_nuke.service.userActionLog(CGConfig_nuke.userName, CGConfig_nuke.projectName,
                                                CGConfig_nuke.taskName, 'SubmitNuke')
            renderTask = CGConfig_nuke.service.myWFsearchTaskByStage(CGConfig_nuke.taskName, CGConfig_nuke.projectName,
                                                                      '渲染')
            """
            parentProject = CGConfig_nuke.service.myWFGetParentProjectInfo(CGConfig_nuke.projectName)
            projectList = json.loads(CGConfig_nuke.service.myWFGetProjectInfo(CGConfig_nuke.projectName))
            try:
                render = projectList[0]['render']
            except KeyError:
                render = ''
            if render == '':
                render = 'MayaBatch'
            CGConfig_nuke.service.setRazunaURL(parentProject['DBHost'], parentProject['DBPort'], parentProject['appKey'])
            try:
                lightFolderID = CGConfig_nuke.service.makefolder(task['assetFolderID'], CGConfig_nuke.razuna_Light_Dir)
            except KeyError:
                return 0
            lightFileList = CGConfig_nuke.service.getassets_last_all(lightFolderID)
            submitFileList = []
            for lightFile in lightFileList:
                submitFileList.append(lightFile)
            submitTaskList = []
            submitTaskList.append({'_id': task['_id'], 'submitFileList': submitFileList, 'render': render})
            renderClass = panel.value('渲染方式')
            nuke.message(renderClass)
            if panel.value('渲染方式') == '序列渲染并合成':
                renderClass = 0
            elif panel.value('渲染方式') == '序列渲染':
                renderClass = 1
            else:
                renderClass = 2
            CGConfig_nuke.service.renderJobSubmit(CGConfig_nuke.userName, jobName + '+Sequence',
                                                  submitTaskList, 'Sequence', renderClass)
            CGConfig_nuke.service.userActionLog(CGConfig_nuke.userName, CGConfig_nuke.projectName,
                                                CGConfig_nuke.taskName, 'SubmitRenderNuke')

        else:
            return 0


    def unsubmitWindow():
        taskName = CGConfig_nuke.currentRenderTask['name'].split('+')[0]
        lightTask = CGConfig_nuke.service.myWFsearchTaskByStage(taskName, CGConfig_nuke.projectName,
                                                                '灯光')
        result = CGConfig_nuke.service.myWFUnSubmitTask(lightTask[0]['_id'])
        CGConfig_nuke.service.userActionLog(CGConfig_nuke.userName, CGConfig_nuke.projectName,
                                            CGConfig_nuke.taskName, 'unSubmitNuke')

    def setupWindow():
        panel = nuke.Panel('参数设置')
        panel.addSingleLineInput('团队', CGConfig_nuke.teamName)
        panel.addSingleLineInput('存储路径', CGConfig_nuke.storageDir)
        panel.addButton('清除')
        panel.addButton('取消')
        panel.addButton('设置')
        panel.setWidth(400)
        ret = panel.show()
        if ret == 1:
            CGConfig_nuke.teamName = panel.value('团队')
            CGConfig_nuke.storageDir = panel.value('存储路径')
        elif ret == 0:
            CGConfig_nuke.storageDir = panel.value('存储路径')
            if os.path.exists(CGConfig_nuke.storageDir):
                if nuke.ask("是否删除目录?"):
                    shutil.rmtree(CGConfig_nuke.storageDir)
                    os.mkdir(CGConfig_nuke.storageDir)
                CGConfig_nuke.service.userActionLog(CGConfig_nuke.userName, CGConfig_nuke.projectName,
                                                CGConfig_nuke.taskName, 'clearBufferNuke')

    def processNukeFile(scriptFile, destFile, mapList, frameList):
        nuke.tprint(destFile)
        fp_in = open(scriptFile, "r")
        fp_out = open(destFile, "w")
        firstFrame = frameList.split('-')[0]
        lastFrame = frameList.split('-')[1]
        lines = fp_in.readlines()
        n = 0
        while n < len(lines):
            #line = lines[n].strip()
            line = lines[n]
            if line.find('Root') >= 0:
                fp_out.write(line)
                n = n + 1
                line = lines[n]
                while not line.find("}") >= 0:
                    if line.find('name') >= 0:
                        line = ' name ' + destFile
                        line = line + '\n'
                        line = line + 'last_frame ' + lastFrame +'\nlock_range true\n'
                        fp_out.write(line)
                    else:
                        line = lines[n]
                        fp_out.write(line)
                    n = n + 1
                    if n >= len(lines):
                        break
                    line = lines[n]
                line = line + '\n'
                fp_out.write(line)
            elif line.find('Read') >= 0:
                fp_out.write(line)
                n = n + 1
                line = lines[n]
                while not line.find("}") >= 0:
                    if line.find('file') >= 0:
                        path = line.split(' ').pop()
                        if path.find('otherDir') < 0:
                            nuke.tprint(line)
                            line = line.replace('Single', 'Sequence')
                            list = line.split('.')
                            ext = list.pop()
                            seq = list.pop()
                            line = line.replace(seq, '####')
                            nuke.tprint(line)
                            fp_out.write(line)
                        else:
                            if nuke.ask('是否将单张图片在渲染序列时换成图片序列？'+ path):
                                path = nuke.getClipname('获得序列')
                                dir1 = os.path.dirname(path)
                                base = os.path.basename(dir1)
                                dirPath = dir1 + '/' + base
                                if not os.path.exists(dirPath):
                                    os.mkdir(dirPath)
                                fileList = os.listdir(path)
                                for file in fileList:
                                    filePath = path + '/' + file
                                    destFile = dirPath + '/' + file
                                    if not os.path.exists(destFile):
                                        shutil.copy(filePath, destFile)
                                list = file.split('.')
                                ext = list.pop()
                                seq = list.pop()
                                line = ' file ' + os.path.join(dirPath, list[0]) + '.%4d.' + ext
                            """
                            else:
                                nuke.error('path =' + path)
                                file = os.path.basename(path)
                                file = file.strip('\n')
                                dir = os.path.dirname(path)
                                filePath = os.path.join(dir, file)
                                destFile = os.path.join(rootDir, file)
                                nuke.error('destFile =' + destFile)
                                if not os.path.exists(destFile):
                                    shutil.copy(filePath, destFile)
                                line = ' file ' + destFile
                            """
                            line = line + '\n'
                            nuke.error(line)
                            fp_out.write(line)
                    elif line.find('format') >= 0:
                        line = line + '\nlast ' + lastFrame
                        line = line + '\noriglast '+ lastFrame + '\n'
                        fp_out.write(line)
                    else:
                        fp_out.write(line)
                    n = n + 1
                    line = lines[n]
                fp_out.write(line)
            elif line.find('Write') >= 0:
                fp_out.write(line)
                n = n + 1
                line = lines[n]
                while not line.find("}") >= 0:
                    if line.find('file ') >= 0:
                        fn = line.split(' ').pop()
                        line = ' file ' + '/Sequence/' + os.path.basename(fn) + '\n'
                        fp_out.write(line)
                    else:
                        fp_out.write(line)
                    n = n + 1
                    line = lines[n]
                line = line + '\n'
                fp_out.write(line)
            else:
                fp_out.write(line)
            n = n + 1
            if (n < len(lines)):
                line = lines[n]
        fp_in.close()
        fp_out.close()
