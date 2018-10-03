#coding=utf-8
import os
import shutil

def processNukeFile(scriptFile):
    #nuke.error(' open read ' + scriptFile)
    fp_in = open(scriptFile, "r")
    scriptFile_dest = os.path.dirname(scriptFile)
    fname = os.path.basename(scriptFile)
    fname = fname.split('.')[0]
    scriptFile_dest = os.path.join(scriptFile_dest, fname + '_Sequence.nk')
    #nuke.error(scriptFile_dest)
    fp_out = open(scriptFile_dest, "w")

    lines = fp_in.readlines()
    n = 0
    while n < len(lines):
        # line = lines[n].strip()
        line = lines[n]
        if line.find('Root') >= 0:
            fp_out.write(line)
            n = n + 1
            line = lines[n]
            while not line.find("}") >= 0:
                if line.find('name') >= 0:
                    line = ' name ' + scriptFile
                    line = line + '\n'
                    fp_out.write(line)
                    dir = os.path.dirname(scriptFile)

                    fileList = os.listdir(os.path.join(dir, 'Sequence'))
                    for file in fileList:
                        filePath = os.path.join(os.path.join(dir, 'Sequence'), file)
                        if os.path.isdir(filePath):
                            break
                    firstFrame, lastFrame = processDir(filePath)
                elif line.find('first_frame') >= 0:
                    line = ' first_frame ' + str(firstFrame)
                    line = line + '\n'
                    fp_out.write(line)
                elif line.find('last_frame') >= 0:
                    line = ' last_frame ' + str(lastFrame)
                    line = line + '\n'
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
                    fn = line.split(' ').pop()
                    if fn.find('output') >= 0 and fn.find('Single') >= 0:
                        line = line.replace('Single', 'Sequence')
                        list = line.split('.')
                        ext = list.pop()
                        seq = list.pop()
                        line = line.replace(seq, '%4d')
                        fp_out.write(line)
                        fname = line.split(' ').pop()
                        dir = os.path.dirname(fname)
                        firstFrame, lastFrame = processDir(dir)
                    else:
                        fn = fn.strip()
                        print 'fn =', fn
                        if os.path.isfile(fn):
                            destFile = os.path.join(os.path.dirname(scriptFile), os.path.basename(fn))
                            shutil.copy(fn, destFile)
                            line = ' file ' + destFile
                            line = line + '\n'
                            fp_out.write(line)
                        else:
                            #nuke.error('line =' + line)
                            #nuke.error(fn + 'is not exist!!!')
                            print 'is not exist!!!'
                elif line.find('origfirst') >= 0:
                    line = ' origfirst ' + str(firstFrame) + '\n'
                    fp_out.write(line)
                elif line.find('origlast') >= 0:
                    line = ' origlast ' + str(lastFrame) + '\n'
                    fp_out.write(line)
                elif line.find('first') >= 0:
                    line = ' first ' + str(firstFrame) + '\n'
                    fp_out.write(line)
                elif line.find('last') >= 0:
                    line = ' last ' + str(lastFrame) + '\n'
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
                    if fn.find('output') >= 0 and fn.find('Single') >= 0:
                        line = line.replace('Single', 'Sequence')
                        fname = line.split(' ').pop()
                        dir = os.path.dirname(dir)
                        fname = scriptFile.split('.')[0]
                        fname = fname + '.%4d.tga'
                        line = ' file ' + fname +'\n'
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


def processDir(dir):
    #nuke.error('dir =' + dir)
    fileList = os.listdir(dir)
    start = 1000
    end = 0
    for file in fileList:
        # nuke.error(file.split('.')[1])
        num = int(file.split('.')[1])
        if start > num:
            start = num
        if end < num:
            end = num
    return start, end

processNukeFile('R:/RD/HFNL_EP03/output/HFNL_S03C019\HFNL_S03C019.nk')