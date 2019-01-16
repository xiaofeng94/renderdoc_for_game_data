# import renderdoc as rd
import struct

def sampleCode(controller):
  curDraw = pyrenderdoc.CurDrawcall()
  state = controller.GetPipelineState()
  # state = pyrenderdoc.CurPipelineState()

  ## get indices for Vertex input

  # ibuf = state.GetIBuffer()
  # print('byteOffset: %f, byteStride: %f'%(ibuf.byteOffset, ibuf.byteStride))

  # iData = controller.GetBufferData(ibuf.resourceId, 
  #                   ibuf.byteOffset+curDraw.indexOffset*curDraw.indexByteWidth,
  #                   curDraw.numIndices*curDraw.indexByteWidth)
  # print('curDraw.indexOffset: %f, curDraw.numIndices: %f, curDraw.indexByteWidth: %f'
  #         %(curDraw.indexOffset, curDraw.numIndices, curDraw.indexByteWidth))

  # for ii in range(curDraw.numIndices):
  #   startIndx = curDraw.indexByteWidth*ii
  #   endindx = startIndx+curDraw.indexByteWidth
  #   print(int.from_bytes(iData[startIndx:endindx], byteorder='little'))

  ## get indices for Vertex output
  postVS = controller.GetPostVSData(0, 0, renderdoc.MeshDataStage.VSOut)
  iData = controller.GetBufferData(postVS.indexResourceId, postVS.indexByteOffset,
                        curDraw.numIndices*postVS.indexByteStride)
  print('postVS.indexByteOffset: %f, curDraw.numIndices: %f, postVS.indexByteStride: %f'
          %(postVS.indexByteOffset, curDraw.numIndices, postVS.indexByteStride))
  
  ## get data for Vertex output
  buffData = controller.GetBufferData(postVS.vertexResourceId, postVS.indexByteOffset, 0)
  
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

    outVSData.append(curVSPosition)
    print(curVSPosition)

  # reflection = state.GetShaderReflection(renderdoc.ShaderStage.Vertex)
  # outSig = reflection.outputSignature
  # vsPosSig = outSig[0]
  # vsPosSig.semanticIdxName


def loadCapture(filename):
  # Open a capture file handle
  cap = rd.OpenCaptureFile()

  # Open a particular file - see also OpenBuffer to load from memory
  status = cap.OpenFile(filename, '', None)

  # Make sure the file opened successfully
  if status != rd.ReplayStatus.Succeeded:
    raise RuntimeError("Couldn't open file: " + str(status))

  # Make sure we can replay
  if not cap.LocalReplaySupport():
    raise RuntimeError("Capture cannot be replayed")

  # Initialise the replay
  status,controller = cap.OpenCapture(None)

  if status != rd.ReplayStatus.Succeeded:
    raise RuntimeError("Couldn't initialise replay: " + str(status))

  return (cap, controller)

if 'pyrenderdoc' in globals():
  pyrenderdoc.Replay().BlockInvoke(sampleCode)
else:
  cap,controller = loadCapture('test.rdc')

  sampleCode(controller)

  controller.Shutdown()
  cap.Shutdown()