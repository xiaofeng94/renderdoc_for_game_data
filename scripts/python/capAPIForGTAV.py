import sys
if sys.version_info < (3, 4):
  raise RuntimeError('At least Python 3.4 is required')

import os

sys.path.append('E:\\renderdoc\\x64\\Release\\pymodules')
os.environ["PATH"] += os.pathsep + os.path.abspath('E:/renderdoc/x64/Release')

import time
import threading
# import os.path

import numpy as np
import scipy.io as sio
import OpenEXR, Imath

import renderdoc as rd


class GTA5Capture(object):
  """docstring for GTA5Capture"""
  def __init__(self):
    super(GTA5Capture, self).__init__()
    self.cap = rd.OpenCaptureFile()
    self.drawcalls = None
    self.controller = None
    self.projMat = np.zeros([4, 4])
    self.isOpen = False  # whether a file has been opened

  def openLogFile(self, filename):
    if self.isOpen:
      self.closeLogFile()

    self.fileName = filename
    # print(self.fileName)

    # Open a particular file - see also OpenBuffer to load from memory
    status = self.cap.OpenFile(filename, '', None)
    # Make sure the file opened successfully
    if status != rd.ReplayStatus.Succeeded:
      raise RuntimeError("Couldn't open file: " + str(status))
    # Make sure we can replay
    if not self.cap.LocalReplaySupport():
      raise RuntimeError("Capture cannot be replayed")

    # Initialise the replay
    status, self.controller = self.cap.OpenCapture(None)
    if status != rd.ReplayStatus.Succeeded:
      raise RuntimeError("Couldn't initialise replay: " + str(status))

    self.getDrawcalls()
    self.isOpen = True


  def closeLogFile(self):
    if not (self.controller is None):
      self.controller.Shutdown()

    self.drawcalls = None
    self.controller = None
    self.projMat = np.zeros([4, 4])
    self.isOpen = False

  def finishCapture(self):
    self.closeLogFile()
    if not (self.cap is None):
      self.cap.Shutdown()


  def getDrawcalls(self):
    # this call is very important for capturing data
    if self.drawcalls == None:
      self.controller.AddFakeMarkers()
      self.drawcalls = self.controller.GetDrawcalls()

    # print('drawcall num: %d'%len(self.drawcalls))
    return self.drawcalls


  def getColorBufferId(self):
    potentialPassIds = [i for i,call in enumerate(self.drawcalls) if call.name.find('Draw(3)') >= 0]
    # assert(len(potentialPassIds) > 1, 'Found not enough potential final passes for GTAV.')
    finalPassId = potentialPassIds[-2] # last Draw(3) for gta is distorted frame
    # print('finalPassId: %d'%finalPassId)

    finalEventId = self.drawcalls[finalPassId].eventId
    # important!!
    self.controller.SetFrameEvent(finalEventId, False)

    state = self.controller.GetPipelineState()
    outTargets = state.GetOutputTargets()
    colorbuffers = [t for t in outTargets if str(t.resourceId) != '0']

    if len(colorbuffers) > 0:
      return colorbuffers[0].resourceId
    else:
      return None

  def getDepthBufferId(self):
    # # below is not suitable for some Graphics configuration
    # passNum = 4
    # potentialPos = [i for i,call in enumerate(self.drawcalls) if call.name.find('%d Targets + Depth)' % passNum) >= 0]
    # if len(potentialPos) < 1:
    #     return None

    # pChildrenDraws = self.drawcalls[potentialPos[0]].children
    # pChildDraw = pChildrenDraws[-1] # last child contains all depth

    # all the frame has Dispacth(120, 68, 1) just after depth buffer is constructed.
    dispachCall = [call for call in self.drawcalls if call.name.find('Dispatch(120') >= 0]
    if len(dispachCall) < 1:
        return None
    depthCall = dispachCall[-1].previous
    
    self.controller.SetFrameEvent(depthCall.eventId, False)

    state = self.controller.GetPipelineState()
    depthTarget = state.GetDepthTarget()

    # get projection matrix
    if self.projMat[0,0] == 0:
      self.computeProjMat()

    if str(depthTarget.resourceId) == '0' or depthTarget is None:
      print ('{} has no depth target'.format(self.fileName))
      return None
    else:
      return depthTarget.resourceId


  def getProjMatrix(self):
    if self.controller is None:
      print('open log file first.')
      return None

    if self.projMat[0,0] == 0:
      # passNum = 4
      # potentialPos = [i for i,call in enumerate(self.drawcalls) if call.name.find('%d Targets + Depth)' % passNum) >= 0]
      # if len(potentialPos) < 1:
      #     return -1

      # pChildrenDraws = self.drawcalls[potentialPos[0]].children
      # pChildDraw = pChildrenDraws[-1] # last child contains all depth

      # all the frame has Dispacth(120, 68, 1) just after depth buffer is constructed.
      dispachCall = [call for call in self.drawcalls if call.name.find('Dispatch(120') >= 0]
      if len(dispachCall) < 1:
          return None
      depthCall = dispachCall[-1].previous
      
      self.controller.SetFrameEvent(depthCall.eventId, False)

      self.computeProjMat()

    if self.projMat[0,0] == 0:
      return None
    else:
      return self.projMat


  def computeProjMat(self):
    if self.controller is None:
      print('open log file first.')
      return

    state = self.controller.GetPipelineState()
    entry = state.GetShaderEntryPoint(rd.ShaderStage.Pixel)
    ps = state.GetShaderReflection(rd.ShaderStage.Pixel)
    cb = state.GetConstantBuffer(rd.ShaderStage.Pixel, 0, 0)

    cbufferVars = self.controller.GetCBufferVariableContents(ps.resourceId, entry, 0, cb.resourceId, 0)

    PVW = np.zeros([4,4])  # gWorldViewProj
    VW = np.zeros([4,4])   # gWorldView
    hasPVW, hasVW = False, False

    for v in cbufferVars:
      if v.name == 'gWorldViewProj':
        hasPVW = True
        for col in range(v.columns):
          for row in range(v.rows):
            PVW[col, row] = v.value.fv[row*v.columns + col]

      if v.name == 'gWorldView':
        hasVW = True
        for col in range(v.columns):
          for row in range(v.rows):
            VW[col, row] = v.value.fv[row*v.columns + col] 

    if hasPVW and hasVW:
      self.projMat = np.mat(PVW)*np.mat(VW).I
      # print('gWorldViewProj')
      # print(PVW)
      # print('gWorldView')
      # print(VW)
      # print('gProj')
      # print(self.projMat)
      # print('--- end --')


  def saveTexture(self, ResourceId, saveFile):
    if ResourceId is None:
      print('saveTexture resourceId None!!!')
      return False

    saveData = rd.TextureSave()
    saveData.resourceId = ResourceId
    # saveData.comp = rd.CompType.UNorm
    saveData.typeHint = rd.CompType.UNorm
    saveData.channelExtract = -1
    saveData.comp.blackPoint = 0.0
    saveData.comp.whitePoint = 1.0
    saveData.alpha = rd.AlphaMapping.Discard

    fileExt = saveFile.split('.')[-1]

    if fileExt == 'dds' or fileExt == 'DDS':
      saveData.destType = rd.FileType.DDS

    elif fileExt == 'png' or fileExt == 'PNG':
      # saveData.alpha = rd.AlphaMapping.Preserve
      saveData.destType = rd.FileType.PNG

    elif fileExt == 'jpg' or fileExt == 'JPG':
      saveData.jpegQuality = 100
      saveData.destType = rd.FileType.JPG

    elif fileExt == 'bmp' or fileExt == 'BMP':
      saveData.destType = rd.FileType.BMP

    elif fileExt == 'tga' or fileExt == 'TGA':
      saveData.destType = rd.FileType.TGA

    elif fileExt == 'hdr' or fileExt == 'HDR':
      saveData.destType = rd.FileType.HDR

    elif fileExt == 'exr' or fileExt == 'EXR':
      saveData.typeHint = rd.CompType.Depth
      saveData.destType = rd.FileType.EXR

    elif fileExt == 'raw' or fileExt == 'RAW':
      saveData.destType = rd.FileType.RAW

    else:
      print('Cannot handle %s file'%fileExt)
      return False

    self.controller.SaveTexture(saveData, saveFile)
    return True

  def computeDepth(self, DepthExrFile, saveFile):
    exrFile = OpenEXR.InputFile(DepthExrFile)

    dw = exrFile.header()['dataWindow']
    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

    pt = Imath.PixelType(Imath.PixelType.FLOAT)
    depthstr = exrFile.channel('D', pt) # S for stencil and D for depth in channels
    depthNDC = np.fromstring(depthstr, dtype = np.float32)

    exrFile.close()

    # convert NDC coordinate to camera coordinate and get depth
    ############### version #2 end #################
    # this is much faster (1.47s) than #1, 
    # but the results are slight different
    windCoords = np.mat(np.ones((4, size[1]*size[0])))
    for x_i in range(size[1]):
      for y_i in range(size[0]):
        pos = x_i*size[0] + y_i
        windCoords[0, pos] = x_i
        windCoords[1, pos] = y_i
        windCoords[2, pos] = depthNDC[pos]

    wind2NDCMat = np.mat([[2/size[1], 0, 0, -1], 
                          [0, -2/size[0], 0, 1],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]])
    gProjMat = self.getProjMatrix()
    if gProjMat is None:
      return
    gProjMatInv = gProjMat.I

    camCoords = gProjMatInv*wind2NDCMat*windCoords # matrix dot
    camCoords[0,:] = camCoords[0,:]/camCoords[3,:]
    camCoords[1,:] = camCoords[1,:]/camCoords[3,:]
    camCoords[2,:] = camCoords[2,:]/camCoords[3,:]

    depth = np.linalg.norm(camCoords, axis=0)
    depth.shape = (size[1], size[0])
    ############### version #2 end #################


    # ############### version #1 #################
    # depthNDC.shape = (size[1], size[0]) # Numpy arrays are (row, col)

    # depth = np.zeros(depthNDC.shape)

    # gProjMat = self.getProjMatrix()
    # gProjMatInv = gProjMat.I

    # ndcCoord = np.mat(np.ones([4,1]))  # last item is 1
    # for x_i in range(size[1]):
    #   # this loop cost around 0.0312s
    #   for y_i in range(size[0]):
    #     xNDC = x_i*2/size[1] - 1
    #     yNDC = 1 - y_i*2/size[0]

    #     ndcCoord[0,0] = xNDC
    #     ndcCoord[1,0] = yNDC
    #     ndcCoord[2,0] = depthNDC[x_i, y_i]

    #     start1 = time.time()
    #     camCoord = gProjMatInv*ndcCoord
    #     camCoord = camCoord/camCoord[3,0]
    #     # print('matrix time: ',time.time()-start1)

    #     depth[x_i, y_i] = np.linalg.norm(camCoord[:3])
    ############### version #1 end #################

    sio.savemat(saveFile, {'depth':depth, 'gProjMat': gProjMat})


class GTA5DataThread(threading.Thread):
  """docstring for GTA5DataThread"""
  def __init__(self, name, log_file_root, save_dir = '', file_list = []):
    super(GTA5DataThread, self).__init__()
    self.name = name
    self.logFileRoot = log_file_root
    self.saveDir = save_dir
    self.fileList = file_list
    self.saveCount = 0

  def setFileList(self, file_list):
    self.fileList = file_list

  def setSaveDir(self, save_dir):
    self.saveDir = save_dir

  def getSaveCount(self):
    return self.saveCount

  def run(self):
    print('Thread[%s] start working'%self.name)
    filesToDel = list()
    gta5Cap = GTA5Capture()

    self.saveCount = 0
    for fineName in self.fileList:
      if fineName[-4:] == '.rdc':
        filePath = os.path.join(self.logFileRoot, fineName)
        print('Thread[%s] process %s'%(self.name, filePath))

        prefix = fineName[:-4]
        gta5Cap.openLogFile(filePath)
        gta5Cap.saveTexture(gta5Cap.getColorBufferId(), 
                              os.path.join(self.saveDir, '%s_rgb.jpg'%prefix))
        depthOk = gta5Cap.saveTexture(gta5Cap.getDepthBufferId(), 
                                        os.path.join(self.saveDir, '%s_zbuffer.exr'%prefix))
        print('depthOk', str(depthOk))
        if depthOk:
          gta5Cap.computeDepth(os.path.join(self.saveDir, '%s_zbuffer.exr'%prefix),
                                os.path.join(self.saveDir, '%s_depth.mat'%prefix))

        filesToDel.append(filePath)
        self.saveCount += 1

    gta5Cap.finishCapture()

    for item in filesToDel:
      os.remove(item)
      print('Thread[%s] del %s'%(self.name, item))
      
    filesToDel.clear() 
    