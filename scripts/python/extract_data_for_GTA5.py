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
# # gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 'E:/GTAVTempCaptures/py1.jpg')
# # gta5Cap.saveTexture(gta5Cap.getDepthBufferId(), 'E:/GTAVTempCaptures/py1.exr')
# gta5Cap.getProjMatrix()
# gta5Cap.closeLogFile()

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_12.10.24_frame12134.rdc')
# # gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 'E:/GTAVTempCaptures/py2.jpg')
# # gta5Cap.saveTexture(gta5Cap.getDepthBufferId(), 'E:/GTAVTempCaptures/py2.exr')
# print(gta5Cap.getProjMatrix())
# gta5Cap.closeLogFile()

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame7520.rdc')
# gta5Cap.getProjMatrix()

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame8423.rdc')
# gta5Cap.getProjMatrix()

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame9043.rdc')
# gta5Cap.getProjMatrix()

gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame9207.rdc')
gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 'E:/GTAVTempCaptures/frame9207.jpg')
gta5Cap.getProjMatrix()

gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame10981.rdc')
gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 'E:/GTAVTempCaptures/frame10981.jpg')
gta5Cap.getProjMatrix()

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame11257.rdc')
# gta5Cap.getProjMatrix()

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame11713.rdc')
# gta5Cap.getProjMatrix()

# gta5Cap.openLogFile('E:/GTAVTempCaptures/GTA5_2018.08.23_14.02.35_frame12477.rdc')
# gta5Cap.getProjMatrix()

gta5Cap.finishCapture()