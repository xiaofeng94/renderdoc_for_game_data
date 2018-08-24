# not support python2
from capAPIForGTAV import GTA5Capture

# capLogFile = 'E:/GTAVTempCaptures/GTA5_2018.08.22_12.39.38_frame10139.rdc'
# rgbFile = 'E:/GTAVTempCaptures/py123_new_api.jpg'

gta5Cap = GTA5Capture()

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

gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame7520.rdc')
gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 'E:/GTAVTempCaptures/frame7520.jpg')
gta5Cap.saveTexture(gta5Cap.getDepthBufferId(), 'E:/GTAVTempCaptures/frame7520.exr')
gta5Cap.computeDepth('E:/GTAVTempCaptures/frame7520.exr',
                      'E:/GTAVTempCaptures/frame7520_2.mat')

gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame8423.rdc')
gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 'E:/GTAVTempCaptures/frame8423.jpg')
gta5Cap.saveTexture(gta5Cap.getDepthBufferId(), 'E:/GTAVTempCaptures/frame8423.exr')
gta5Cap.computeDepth('E:/GTAVTempCaptures/frame8423.exr',
                      'E:/GTAVTempCaptures/frame8423_2.mat')

gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame9043.rdc')
gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 'E:/GTAVTempCaptures/frame9043.jpg')
gta5Cap.saveTexture(gta5Cap.getDepthBufferId(), 'E:/GTAVTempCaptures/frame9043.exr')
gta5Cap.computeDepth('E:/GTAVTempCaptures/frame9043.exr',
                      'E:/GTAVTempCaptures/frame9043_2.mat')

gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame9207.rdc')
gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 'E:/GTAVTempCaptures/frame9207.png')
gta5Cap.saveTexture(gta5Cap.getDepthBufferId(), 'E:/GTAVTempCaptures/frame9207.exr')
gta5Cap.computeDepth('E:/GTAVTempCaptures/frame9207.exr',
                      'E:/GTAVTempCaptures/frame9207_2.mat')
# gta5Cap.getProjMatrix()

gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame10981.rdc')
gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 'E:/GTAVTempCaptures/frame10981.jpg')
gta5Cap.saveTexture(gta5Cap.getDepthBufferId(), 'E:/GTAVTempCaptures/frame10981.exr')
gta5Cap.computeDepth('E:/GTAVTempCaptures/frame10981.exr',
                      'E:/GTAVTempCaptures/frame10981_2.mat')

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame11257.rdc')
# gta5Cap.getProjMatrix()

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame11713.rdc')
# gta5Cap.getProjMatrix()

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame12477.rdc')
# gta5Cap.getProjMatrix()

gta5Cap.finishCapture()