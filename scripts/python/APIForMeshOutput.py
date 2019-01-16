import sys
if sys.version_info < (3, 4):
  raise RuntimeError('At least Python 3.4 is required')

import os
import numpy as np
import struct
import time

sys.path.append('E:\\renderdoc\\x64\\Release\\pymodules')
os.environ["PATH"] += os.pathsep + os.path.abspath('E:/renderdoc/x64/Release')

import renderdoc as rd

class GTAVMeshCapture(object):
  """docstring for GTAVMeshCapture"""
  def __init__(self, height, width, distThr):
    super(GTAVMeshCapture, self).__init__()
    self.cap = rd.OpenCaptureFile()
    self.controller = None
    self.drawcalls = None
    self.height = height
    self.width = width

    self.dist_threshold = distThr
    
  def openLogFile(self, filename):
    if self.isFileOpened():
      self.closeLogFile()

    self.fileName = filename
    # print(self.fileName)

    # Open a particular file - see also OpenBuffer to load from memory
    status = self.cap.OpenFile(filename, '', None)
    # Make sure the file opened successfully
    if status != rd.ReplayStatus.Succeeded:
      print("Couldn't open file: " + str(status))
    # Make sure we can replay
    if not self.cap.LocalReplaySupport():
      print("Capture cannot be replayed")

    # Initialise the replay
    status, self.controller = self.cap.OpenCapture(None)
    if status != rd.ReplayStatus.Succeeded:
      print("Couldn't initialise replay: " + str(status))

    self.getDrawcalls()

  def closeLogFile(self):
    if self.controller is not None:
      self.controller.Shutdown()

    self.controller = None
    self.drawcalls = None

  def isFileOpened(self):
    if self.controller is None:
      return False
    if self.cap is None:
      return False

    return True

  def getDrawcalls(self):
    if self.isFileOpened():
      # self.controller.AddFakeMarkers() # arrange drawcalls in group
      self.drawcalls = self.controller.GetDrawcalls()
      return self.drawcalls
    else:
      print('open log file first.')
      return list()

  def saveRGBImage(self, save_path):
    isOK = self.saveTexture(self.getColorBufferId(), save_path)
    return isOK


  def getColorBufferId(self):
    if not self.isFileOpened():
      print('open log file first.')
      return None

    # the input of last draw(3) is the desired one
    potentialCalls = [call for call in self.drawcalls if call.name.find('Draw(3)') >= 0]
    
    finalCall = potentialCalls[-1]
    finalEventId = finalCall.eventId

    self.controller.SetFrameEvent(finalEventId, False)

    inputRes = self.getInputResources()
    if len(inputRes) > 0:
      return inputRes[0].resourceId
    else:
      return None


  def getInputResources(self):
    if not self.isFileOpened():
      print('open log file first.')
      return list()

    state = self.controller.GetPipelineState()
    stage = rd.ShaderStage.Pixel

    mappings = state.GetBindpointMapping(stage)
    readOnlyRes = state.GetReadOnlyResources(stage)

    if mappings is None:
      return list()
    inMappings = mappings.readOnlyResources

    inResList = list()
    for inMap in inMappings:
      key = inMap.bind
      # bindPoint in readOnlyRes seems identical to index of the position
      if readOnlyRes[key].bindPoint.bind == key:
        resArray = readOnlyRes[key].resources

        # gui only take the frist element in resArray for efficiency.
        inResList.append(resArray[0])
      else:
        print('unordered readOnlyRes !!')
        for idx in range(len(readOnlyRes)):
          if readOnlyRes[idx].bindPoint.bind == key:
            resArray = readOnlyRes[idx].resources
            inResList.append(resArray[0])
            break

    return inResList


  def getDepthBufferId(self):
    if not self.isFileOpened():
      print('open log file first.')
      return None
    
    # all the frame has Dispacth(120, 68, 1) just after depth buffer is constructed.
    dispachCall = [call for call in self.drawcalls if call.name.find('Dispatch(120') >= 0]
    if len(dispachCall) < 1:
        return None
    depthCall = dispachCall[-1].previous

    self.controller.SetFrameEvent(depthCall.eventId, False)

    state = self.controller.GetPipelineState()
    depthTarget = state.GetDepthTarget()

    if str(depthTarget.resourceId) == '0' or depthTarget is None:
      print ('{} has no depth target'.format(self.fileName))
      return None
    else:
      return depthTarget.resourceId

  def getDepthInNDC(self):
    depthId = self.getDepthBufferId()
    depthRaw = self.controller.GetTextureData(depthId, 0, 0)

    # # find the texture description for depth
    # texDescripts = self.controller.GetTextures()
    # print(len(texDescripts))
    # for tex in texDescripts:
    #   if tex.resourceId == depthId:
    #     depthTex = tex
    #     break

    # depthRaw 4 bytes depth + 4 bytes stencil.
    # depth values stay in NDC and thus range [0,1].
    # Note that a large value for depth in NDC is near.
    depthMap = np.zeros((self.height, self.width))
    for r_dp in range(self.height):
      for c_dp in range(self.width):
        byte_start = 8*(r_dp*self.width+c_dp)
        depthMap[r_dp,c_dp] = struct.unpack('f', 
                                depthRaw[byte_start:byte_start+4])[0]
    return depthMap


  def getMeshOutputs(self, carPedOnly = False):
    # The render process of interest start with 
    # 4 ClearRenderTargetView and one ClearDepthStencilView.
    # It ends with Dispatch(120,68,1). 
    # Note that the number in Dispatch correlates with resolutions of the screen

    startT = time.time()

    # locate the start of the render process
    startCall = None
    for call in self.drawcalls:
      if 'ClearRenderTargetView' in call.name:
        nextCall = call.next
        next2Call = call.next.next
        next3Call = call.next.next.next
        if ((nextCall and 'ClearRenderTargetView' in nextCall.name) and
            (next2Call and 'ClearRenderTargetView' in next2Call.name) and
            (next3Call and 'ClearRenderTargetView' in next3Call.name)):
          startCall = next3Call.next.next
          break

    # transformation matrices for all objects
    mtxArrayList = [] 
    # list of mesh data for all objects. 
    # meshes with the very similar transformation matrices as an object
    outVSArrayList = [] 
    # list of the number of mesh in a object.
    outVSNumList = []
    # list of types of objects.
    outVSTypeList = []

    curDraw = startCall
    curMask = np.zeros([self.height, self.width], dtype = np.uint8)
    while curDraw and ('Dispatch(120' not in curDraw.name):
    # for drawId in range(2):
      self.controller.SetFrameEvent(curDraw.eventId, False)

      state = self.controller.GetPipelineState()
      entry = state.GetShaderEntryPoint(rd.ShaderStage.Pixel)
      curRef = state.GetShaderReflection(rd.ShaderStage.Vertex)

      curConstBlocks = self.getConstBlocks()

      if len(curConstBlocks) <= 2:
        # if len(curConstBlocks) <= 2, the obj is not very important
        curDraw = curDraw.next
        continue

      # objType: 0 for unknown object
      # 1 for pedestrian
      # 2 for vehicle
      objType = 0
      rageMtxBlockId = -1
      matWheelBlockId = -1
      for idx, block in enumerate(curConstBlocks):
        if 'ped_common_shared_locals' == block.name:
          objType = 1
        if 'vehicle_globals' == block.name:
          objType = 2
        if 'matWheelBuffer' == block.name:
          matWheelBlockId = idx
        if 'rage_matrices' == block.name:
          rageMtxBlockId = idx

      # get transformation matrix
      if matWheelBlockId >= 0:
        BufIdx = matWheelBlockId
      elif rageMtxBlockId >= 0:
        BufIdx = rageMtxBlockId
      else:
        BufIdx = 0

      curConstBuf = state.GetConstantBuffer(rd.ShaderStage.Vertex, BufIdx, 0)
      cbufferVars = self.controller.GetCBufferVariableContents(curRef.resourceId, 
                                      entry, BufIdx, curConstBuf.resourceId, 0)
      
      if matWheelBlockId >= 0 and 'matWheelWorldViewProj' == cbufferVars[1].name:
        mtxArray = self.getMatrixInBuff(cbufferVars[1])
      elif rageMtxBlockId >= 0 and 'gWorldViewProj' == cbufferVars[2].name:
        mtxArray = self.getMatrixInBuff(cbufferVars[2])
      else:
        print('no projection matrix !!!')
        mtxArray = np.zeros((4, 4))

      # ensure whether there is a transformation matrix in mtxArrayList
      objId = self.isInMtxArrayList(mtxArray, mtxArrayList)

      if carPedOnly and (objType == 0):
        # known type
        curDraw = curDraw.next
        continue

      print('%s, proccess as type %d'%(curDraw.name, objType))

      if matWheelBlockId >= 0:
      # if objType == 2:
        curDraw, outVSArray = self.getTyreMeshData(curDraw)
        # if objId == -1, it means the last object in the list
        print('same objId: %d'%objId)
        outVSArrayList[objId] = np.append(outVSArrayList[objId], outVSArray, axis=0)
        outVSNumList[objId] += 1

      else:
        outVSArray = self.getCurMeshData(curDraw)
        if len(outVSArray) > 0:
          if objId >= 0:
            if objId != 1 or (objId == 1 and (objId == (len(mtxArrayList)-1))):
              print('same objId: %d'%objId)
              outVSArrayList[objId] = np.append(outVSArrayList[objId], outVSArray, axis=0)
              outVSNumList[objId] += 1

          else:
            print('new objId: %d'%len(outVSTypeList))
            mtxArrayList.append(mtxArray)
            outVSArrayList.append(outVSArray)
            outVSNumList.append(1)
            outVSTypeList.append(objType) #

        curDraw = curDraw.next

    print('elapsed time: %f'%(time.time() - startT))

    return outVSTypeList, mtxArrayList, outVSArrayList, outVSNumList


  def isInMtxArrayList(self, mtxArray, mtxArrayList):
    objId = -1
    for mxtId, tempMtx in enumerate(mtxArrayList):
      mtxDiff = np.mean(np.abs(tempMtx-mtxArray))
      if mtxDiff < 0.01:
        objId = mxtId

    return objId


  def getConstBlocks(self):
    # get info for Constant buffer, not the data of Constant buffer
    state = self.controller.GetPipelineState()
    curRef = state.GetShaderReflection(rd.ShaderStage.Vertex)
    curConstBlocks = curRef.constantBlocks

    return curConstBlocks


  def getTyreMeshData(self, curDraw):
    # get all mesh data of a car and return those data with the last drawcall 
    curCarDraw = curDraw

    carMeshData = np.zeros([0,4])
    while curCarDraw:
      self.controller.SetFrameEvent(curCarDraw.eventId, False)

      curConstBlocks = self.getConstBlocks()

      isDrawTyre = False
      for idx, block in enumerate(curConstBlocks):
        if 'matWheelBuffer' == block.name:
          isDrawTyre = True
          break

      if not isDrawTyre:
        return curCarDraw, carMeshData

      # print('--car: %s'%curCarDraw.name)
      tempMeshData = self.getCurMeshData(curCarDraw)
      carMeshData = np.append(carMeshData, tempMeshData, axis=0)

      curCarDraw = curCarDraw.next

    return curCarDraw, carMeshData


  def getMatrixInBuff(self, mtxBuf):
    mtxArray = np.zeros((mtxBuf.rows, mtxBuf.columns))
    for mtx_r in range(mtxBuf.rows):
      for mtx_c in range(mtxBuf.columns):
        mtxArray[mtx_r,mtx_c] = mtxBuf.value.fv[mtx_r*mtxBuf.columns + mtx_c]
    return mtxArray


  def getCurMeshData(self, curDraw):
    # if the mesh is too far away, it can be ignored
    # get indices for Vertex output
    postVS = self.controller.GetPostVSData(0, 0, rd.MeshDataStage.VSOut)
    iData = self.controller.GetBufferData(postVS.indexResourceId, postVS.indexByteOffset,
                          curDraw.numIndices*postVS.indexByteStride)
    # print('postVS.indexByteOffset: %f, curDraw.numIndices: %f, postVS.indexByteStride: %f'
    #     %(postVS.indexByteOffset, curDraw.numIndices, postVS.indexByteStride))

    # get data for Vertex output
    buffData = self.controller.GetBufferData(postVS.vertexResourceId, postVS.indexByteOffset, 0)
    
    outStride = postVS.vertexByteStride

    outVSData = []
    for ii in range(curDraw.numIndices):
      indxStart = postVS.indexByteStride*ii
      indxEnd = indxStart+postVS.indexByteStride
      curIndx = int.from_bytes(iData[indxStart:indxEnd], byteorder='little')

      outStart = outStride*curIndx

      curVSPosition = [0,0,0,0] # (x,y,z,w)
      for i_pos in range(len(curVSPosition)):
        curVSPosition[i_pos] = struct.unpack('f', buffData[outStart:outStart+4])[0]
        # int.from_bytes(buffData[outStart:outStart+4], byteorder='little')
        outStart += 4

      # whether a vertex is far away
      if curVSPosition[3] > self.dist_threshold: 
        print('mesh is too far')
        return np.zeros([0,4])

      outVSData.append(curVSPosition)
      # print(curVSPosition)

    if len(outVSData) == 0:
      outVSArray = np.zeros([0,4])
    else:
      outVSArray = np.array(outVSData)

    return outVSArray

  def saveTexture(self, ResourceId, saveFile):
    if not self.isFileOpened():
      print('open log file first.')
      return False

    if ResourceId is None:
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