import sys
if sys.version_info < (3, 4):
  raise RuntimeError('At least Python 3.4 is required')

import os

sys.path.append('E:\\renderdoc\\x64\\Release\\pymodules')
os.environ["PATH"] += os.pathsep + os.path.abspath('E:/renderdoc/x64/Release')

import renderdoc as rd
import numpy as np

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
    print(self.fileName)

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
    self.controller.Shutdown()
    self.drawcalls = None
    self.controller = None
    self.projMat = np.zeros([4, 4])
    self.isOpen = False

  def finishCapture(self):
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

    return colorbuffers[0].resourceId

  def getDepthBufferId(self):
    passNum = 4
    potentialPos = [i for i,call in enumerate(self.drawcalls) if call.name.find('%d Targets + Depth)' % passNum) >= 0]
    if len(potentialPos) < 1:
        return -1

    pChildrenDraws = self.drawcalls[potentialPos[0]].children
    pChildDraw = pChildrenDraws[-1] # last child contains all depth

    self.controller.SetFrameEvent(pChildDraw.eventId, False)

    state = self.controller.GetPipelineState()
    depthTarget = state.GetDepthTarget()

    # get projection matrix
    if self.projMat[0,0] == 0:
      self.computeProjMat()

    if str(depthTarget.resourceId) == '0':
      print ('{} has no depth target'.format(self.fileName))
      return None
    else:
      return depthTarget.resourceId


  def getProjMatrix(self):
    if self.projMat[0,0] == 0:
      passNum = 4
      potentialPos = [i for i,call in enumerate(self.drawcalls) if call.name.find('%d Targets + Depth)' % passNum) >= 0]
      if len(potentialPos) < 1:
          return -1

      pChildrenDraws = self.drawcalls[potentialPos[0]].children
      pChildDraw = pChildrenDraws[-1] # last child contains all depth

      self.controller.SetFrameEvent(pChildDraw.eventId, False)

      self.computeProjMat()

    return self.projMat


  def computeProjMat(self):
    state = self.controller.GetPipelineState()
    entry = state.GetShaderEntryPoint(rd.ShaderStage.Pixel)
    ps = state.GetShaderReflection(rd.ShaderStage.Pixel)
    cb = state.GetConstantBuffer(rd.ShaderStage.Pixel, 0, 0)

    cbufferVars = self.controller.GetCBufferVariableContents(ps.resourceId, entry, 0, cb.resourceId, 0)

    PVW = np.zeros([4,4])  # gWorldViewProj
    VW = np.zeros([4,4])   # gWorldView
    hasPVW = False
    hasVW = False

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
      self.projMat = np.array(np.mat(PVW)*np.mat(VW).I)
      # print('gWorldViewProj')
      # print(PVW)
      # print('gWorldView')
      # print(VW)
      print('gProj')
      print(self.projMat)
      print('--- end --')


  def saveTexture(self, ResourceId, saveFile):
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
      saveData.alpha = rd.AlphaMapping.Preserve
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


