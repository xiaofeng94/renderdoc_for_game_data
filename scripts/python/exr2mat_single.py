# convert to .mat

import OpenEXR, Imath
import os.path
import scipy.io as sio
import numpy as np

depth_save_root = 'E:/GTAVTempCaptures/'
exr_depth_file = 'E:/GTAVTempCaptures/py1.exr'
filePrefix = 'py1'

exrFile = OpenEXR.InputFile(exr_depth_file)
dw = exrFile.header()['dataWindow']
size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

pt = Imath.PixelType(Imath.PixelType.FLOAT)
depthstr = exrFile.channel('D', pt) # S for stencil and D for depth in channels
depth = np.fromstring(depthstr, dtype = np.float32)
depth.shape = (size[1], size[0]) # Numpy arrays are (row, col)

sio.savemat('{0}/{1}_depth.mat'.format(depth_save_root,filePrefix), {'depth':depth})

exrFile.close()
