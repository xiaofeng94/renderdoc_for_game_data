import numpy as np
import cv2
import scipy.io as sio

from APIForMeshOutput import GTAVMeshCapture

def isObjStrange(objVS):
  # object should be dropped if it's too small, too large or too long
  if len(objVS) == 0:
    return True

  retFlag = False

  z_Dist = objVS[:,3]
  x_NDCs = objVS[:,0]/z_Dist
  y_NDCs = objVS[:,1]/z_Dist

  rateInX = (np.max(x_NDCs) - np.min(x_NDCs))/2 # dimension in x([-1,1]) axis
  rateInY = (np.max(y_NDCs) - np.min(y_NDCs))/2 # dimension in y([-1,1]) axis
  distInZ = np.max(z_Dist) - np.min(z_Dist) # in meters

  print('isObjStrange(%f,%f,%f,%f)'%(rateInX,rateInY,distInZ,np.max(z_Dist)))

  if rateInX < 0.02 and rateInY < 0.02:
    retFlag = True
  if rateInX < 0.01:
    retFlag = True
  if rateInY < 0.01:
    retFlag = True
  if distInZ > 15: # in meters
    retFlag = True
  # too large obj
  if rateInX+rateInY > 5:
    retFlag = True

  return retFlag

def isRealPedestrian(meshNumInObj):
  return (meshNumInObj > 1)

def isTotalOccluded(objVS, depthMap):
  # depthmap in NDC, the larger value, the nearer distance.
  height, width = depthMap.shape[0:2]

  apCount = 0 # the number of vertices appeared in view
  for vsPos in objVS:
    x_NDC,y_NDC,z_NDC = vsPos[:3]/vsPos[3]

    if ((-1 <= x_NDC and x_NDC <= 1) and 
        (-1 <= y_NDC and y_NDC <= 1) and
        (0 <= z_NDC and z_NDC <= 1) ):
      x_win = int(width/2.0*x_NDC+width/2.0)
      y_win = int(height/(-2.0)*y_NDC+height/2.0)
      # print('NDC(%f, %f)'%(x_NDC,y_NDC))
      # print('win(%d, %d)'%(x_win,y_win))
      if depthMap[y_win, x_win] <= z_NDC:
        apCount += 1

  # the rate of the number of vertices appeared in view
  apRate = float(apCount)/len(objVS)
  print('isTotalOccluded(%s)'%apRate)
  if apRate > 0.005:
    return False
  else:
    return True

def fillMask(curMask, outVSArray, fillVal, dimension):
  # draw the mask
  # outVSArray should be [[x_0,y_0,z_0,w_0],[x_1,y_1,z_1,w_1],...]
  width,height = dimension[:2]

  outVSArrayNum = len(outVSArray)
  for ii in range(int(outVSArrayNum/3)):
    triangle = outVSArray[3*ii:3*ii+3,:2]

    triangle[0,:] = triangle[0,:]/outVSArray[3*ii,3]
    triangle[1,:] = triangle[1,:]/outVSArray[3*ii+1,3]
    triangle[2,:] = triangle[2,:]/outVSArray[3*ii+2,3]

    # x axis of NDC in view ranges [-1,1]; 
    # y axis of NDC in view ranges [-1,1].
    # convert NDC to windows coordinates
    triangle[:,0] = width/2.0*triangle[:,0]+width/2.0
    triangle[:,1] = height/-2.0*triangle[:,1]+height/2.0

    triangle = triangle[np.newaxis,...]
    triangle = triangle.astype(int)
    # print(triangle)

    cv2.fillPoly(curMask, triangle, fillVal)
    
  return curMask

### configuration ###
log_file = 'E:/GTA5_Data/GTA5_2019.01.13_13.23.32_frame5922.rdc'

winHeight = 1080
winWidth = 1920
distThreshold = 200 # in meters
car_ped_only = True # set false if you want to get all entities

savePath = './capture_RGB_image.png'
### configuration ###

print('------- create capture object -------')
# Note that multiple capture objects can be created at the same time
# You may process your data in multiple threads or multiple processes.
cap = GTAVMeshCapture(winHeight, winWidth, distThreshold)
print('loading file...')
cap.openLogFile(log_file)

print('------- save RGB image -------')
print('save RGB image to %s'%savePath)
cap.saveRGBImage(savePath)

print('------- get mesh data -------')
objTypeList, objMtxList, objVSList, objVSNumList = cap.getMeshOutputs(car_ped_only)
depthMap = cap.getDepthInNDC()

print('------- render mesh outputs -------')
normObjCount = 0
typeNames = ['unknown', 'pedestrain', 'car']
masks = np.zeros([0, winHeight, winWidth], dtype = np.uint8)
labelList = []
for indx in range(len(objTypeList)):
  objType = objTypeList[indx]
  vsNum = objVSNumList[indx]
  typeName = typeNames[objType]

  print('-- No. %d, type(%s), vsNum(%d)'%(indx, typeName, vsNum))
  
  objVS = objVSList[indx]
  if isObjStrange(objVS):
    print('strange object')
    continue

  if isTotalOccluded(objVS, depthMap):
    print('occluded object')
    continue

  if (objType == 1) and (not isRealPedestrian(vsNum)):
    print('a wrong pedestrian')
    continue

  mask = np.zeros([winHeight, winWidth], dtype = np.uint8)
  mask = fillMask(mask, objVSList[indx], 255,[winWidth,winHeight])

  print('normal object')
  normObjCount += 1
  masks = np.append(masks, mask[np.newaxis,...], axis=0)
  labelList.append(objType)

  cv2.imshow(typeName, mask)
  cv2.waitKey(0)

print('----------- statistic -------')
print('Normal object count: %d'%normObjCount)

sio.savemat('masks.mat', {'masks':masks, 'labels':labelList})