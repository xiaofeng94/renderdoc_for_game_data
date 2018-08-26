# not support python2
from capAPIForGTAV import GTA5Capture
import keyboard

import os, time


isActive = True

log_file_root = 'F:/GTAVTempCaptures'
save_root = 'E:/GTA5_Data'

# when file count > save_num, extract data from those log files
save_num = 500
totalSaveCount = 0


def safeClose(event):
  global gta5Cap, isActive

  print('quit data procesing..')
  isActive = False

if __name__ == '__main__':
  keyboard.on_release_key('q', safeClose)
  filesToDel = list()

  while isActive:
    curFileCount = 0
    currFileList = os.listdir(log_file_root)
    for fineName in currFileList:
      if fineName[-4:] == '.rdc':
        curFileCount += 1

    if curFileCount > save_num:
      gta5Cap = GTA5Capture()
      # extract data and delete log files
      saveDir = os.path.join(save_root, '%d_%d'%(totalSaveCount+1, totalSaveCount+save_num))
      if not os.path.exists(saveDir):
        os.makedirs(saveDir)

      saveCount = 0
      for fineName in currFileList:
        if fineName[-4:] == '.rdc':
          filePath = os.path.join(log_file_root, fineName)
          print('process %s'%filePath)

          prefix = fineName[:-4]
          gta5Cap.openLogFile(filePath)
          gta5Cap.saveTexture(gta5Cap.getColorBufferId(), os.path.join(saveDir, '%s_rgb.jpg'%prefix))
          gta5Cap.saveTexture(gta5Cap.getDepthBufferId(), os.path.join(saveDir, '%s_zbuffer.exr'%prefix))
          gta5Cap.computeDepth(os.path.join(saveDir, '%s_zbuffer.exr'%prefix),
                                os.path.join(saveDir, '%s_depth.mat'%prefix))

          filesToDel.append(filePath)
          saveCount += 1
          
        if saveCount >= save_num:
          break

      gta5Cap.finishCapture()
      for idx, item in enumerate(filesToDel):
        os.remove(item)
        print('delete %s'%item)
        
      filesToDel.clear()

      totalSaveCount += saveCount

    else:
      print('Curr file count: %s (press q to quit)'%curFileCount)
      time.sleep(1)

  keyboard.unhook_all()

# capLogFile = 'E:/GTAVTempCaptures/GTA5_2018.08.22_12.39.38_frame10139.rdc'
# rgbFile = 'E:/GTAVTempCaptures/py123_new_api.jpg'

# gta5Cap = GTA5Capture()

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame7520.rdc')
# gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 'E:/GTAVTempCaptures/py2.jpg')
# gta5Cap.saveTexture(gta5Cap.getDepthBufferId(), 'E:/GTAVTempCaptures/py2.exr')
# gta5Cap.getProjMatrix()
# gta5Cap.closeLogFile()

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_12.10.24_frame11828.rdc')
# gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 'E:/GTAVTempCaptures/frame11828.jpg')
# gta5Cap.saveTexture(gta5Cap.getDepthBufferId(), 'E:/GTAVTempCaptures/frame11828.exr')
# gta5Cap.computeDepth('E:/GTAVTempCaptures/frame11828.exr',
#                       'E:/GTAVTempCaptures/frame11828_2.mat')

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_12.10.24_frame12134.rdc')
# # gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 'E:/GTAVTempCaptures/py2.jpg')
# # gta5Cap.saveTexture(gta5Cap.getDepthBufferId(), 'E:/GTAVTempCaptures/py2.exr')
# print(gta5Cap.getProjMatrix())
# gta5Cap.closeLogFile()

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame7520.rdc')
# gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 'E:/GTAVTempCaptures/frame7520.jpg')
# gta5Cap.saveTexture(gta5Cap.getDepthBufferId(), 'E:/GTAVTempCaptures/frame7520.exr')
# gta5Cap.computeDepth('E:/GTAVTempCaptures/frame7520.exr',
#                       'E:/GTAVTempCaptures/frame7520_2.mat')

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame8423.rdc')
# gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 'E:/GTAVTempCaptures/frame8423.jpg')
# gta5Cap.saveTexture(gta5Cap.getDepthBufferId(), 'E:/GTAVTempCaptures/frame8423.exr')
# gta5Cap.computeDepth('E:/GTAVTempCaptures/frame8423.exr',
#                       'E:/GTAVTempCaptures/frame8423_2.mat')

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame9043.rdc')
# gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 'E:/GTAVTempCaptures/frame9043.jpg')
# gta5Cap.saveTexture(gta5Cap.getDepthBufferId(), 'E:/GTAVTempCaptures/frame9043.exr')
# gta5Cap.computeDepth('E:/GTAVTempCaptures/frame9043.exr',
#                       'E:/GTAVTempCaptures/frame9043_2.mat')

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame9207.rdc')
# gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 'E:/GTAVTempCaptures/frame9207.png')
# gta5Cap.saveTexture(gta5Cap.getDepthBufferId(), 'E:/GTAVTempCaptures/frame9207.exr')
# gta5Cap.computeDepth('E:/GTAVTempCaptures/frame9207.exr',
#                       'E:/GTAVTempCaptures/frame9207_2.mat')

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame10981.rdc')
# gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 'E:/GTAVTempCaptures/frame10981.jpg')
# gta5Cap.saveTexture(gta5Cap.getDepthBufferId(), 'E:/GTAVTempCaptures/frame10981.exr')
# gta5Cap.computeDepth('E:/GTAVTempCaptures/frame10981.exr',
#                       'E:/GTAVTempCaptures/frame10981_2.mat')


# gta5Cap.finishCapture()