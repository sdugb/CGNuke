# coding=utf-8
import nuke
import os
import json
from nukescripts import panels
# import PySide.QtCore as QtCore
# import PySide.QtGui as QtGui
import CGNuke
import CGConfig_nuke

def Login():
    service = CGNuke.CGService_nuke.DAMService()

    CGConfig_nuke.configFilePath = CGConfig_nuke.sysStorageDir + '/' + CGConfig_nuke.ConfigFileName
    if os.path.exists(CGConfig_nuke.configFilePath):
        fp = open(CGConfig_nuke.configFilePath, 'r')
        config = json.load(fp)
        fp.close()
        CGConfig_nuke.userName = config['userName']
        CGConfig_nuke.password = config['password']
        CGConfig_nuke.teamName = config['teamName']

    if CGNuke.CGDialog_nuke.loginWindow(service) == '0':
        menubar = nuke.menu('Nuke')
        menubar.findItem('RCMenu/登录账号').setEnabled(False)
        menubar.findItem('RCMenu/退出账号').setEnabled(True)
        menubar.findItem('RCMenu/打开单帧任务').setEnabled(True)
        menubar.findItem('RCMenu/查看序列结果').setEnabled(True)
        menubar.findItem('RCMenu/打开序列任务').setEnabled(True)
        #CGNuke.RCDialog_nuke.openWindow()

def Logout():
    nuke.error('Logout')
    menubar = nuke.menu('Nuke')
    menubar.findItem('RCMenu/退出账号').setEnabled(False)
    menubar.findItem('RCMenu/打开单帧任务').setEnabled(False)
    menubar.findItem('RCMenu/查看序列结果').setEnabled(False)
    menubar.findItem('RCMenu/打开序列任务').setEnabled(False)
    menubar.findItem('RCMenu/保存任务').setEnabled(False)
    menubar.findItem('RCMenu/提交渲染').setEnabled(False)
    menubar.findItem('RCMenu/退回任务').setEnabled(False)
    menubar.findItem('RCMenu/登录账号').setEnabled(True)
    nuke.scriptClear()
    fp = open(CGConfig_nuke.configFilePath, 'w')
    config = {'userName': CGConfig_nuke.userName,
              'password': CGConfig_nuke.password,
              'teamName': CGConfig_nuke.teamName
              }
    json.dump(config, fp)
    fp.close()

def Open():
    while (CGNuke.RCDialog_nuke.openWindow('Single')):
        pass

def OpenSequence():
    while (CGNuke.RCDialog_nuke.openWindow('Sequence')):
        pass

def OpenSequenceResult():
    while (CGNuke.RCDialog_nuke.openSequenceResultWindow()):
        pass

def Save():
    nuke.error('Save')
    CGNuke.RCDialog_nuke.saveWindow()

def Submit():
    nuke.error('submit')
    CGNuke.RCDialog_nuke.submitWindow()

def Execute():
    nuke.error('begin')
    CGNuke.RCDialog_nuke.executeWindow()

def unSubmit():
    nuke.error('unsubmit')
    CGNuke.RCDialog_nuke.unsubmitWindow()

def Setup():
    CGNuke.RCDialog_nuke.setupWindow()

def start():
    CGNuke.CGConfig_nuke.storageDir = CGNuke.CGConfig_nuke.outputPath + 'nuke'
    nuke.error(CGNuke.CGConfig_nuke.storageDir)
    if not os.path.exists(CGNuke.CGConfig_nuke.storageDir):
        os.mkdir(CGNuke.CGConfig_nuke.storageDir)

    CGConfig_nuke.configFilePath = CGConfig_nuke.storageDir + '/' + CGConfig_nuke.ConfigFileName
    if os.path.exists(CGConfig_nuke.configFilePath):
        fp = open(CGConfig_nuke.configFilePath, 'r')
        config = json.load(fp)
        fp.close()
        CGConfig_nuke.userName = config['userName']
        CGConfig_nuke.password = config['password']
        CGConfig_nuke.teamName = config['teamName']

    menubar = nuke.menu('Nuke')
    m = menubar.addMenu('RCMenu')
    m.addCommand('登录账号', Login)
    m.addCommand('退出账号', Logout)
    m.addSeparator()
    m.addCommand('打开单帧任务', Open)
    m.addCommand('打开序列任务', OpenSequence)
    m.addCommand('查看序列结果', OpenSequenceResult)
    m.addCommand('保存任务', Save)
    m.addSeparator()
    m.addCommand('提交渲染', Submit)
    m.addCommand('退回任务', unSubmit)
    m.addSeparator()
    m.addCommand('设置参数', Setup)

    menubar.findItem('RCMenu/退出账号').setEnabled(False)
    menubar.findItem('RCMenu/打开单帧任务').setEnabled(False)
    menubar.findItem('RCMenu/查看序列结果').setEnabled(False)
    menubar.findItem('RCMenu/打开序列任务').setEnabled(False)
    menubar.findItem('RCMenu/保存任务').setEnabled(False)
    menubar.findItem('RCMenu/提交渲染').setEnabled(False)
    menubar.findItem('RCMenu/退回任务').setEnabled(False)


