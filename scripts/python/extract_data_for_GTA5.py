# not support python2
from capAPIForGTAV import GTA5Capture, GTA5DataThread
import keyboard

import os, time


isActive = True

log_file_root = 'F:/GTAVTempCaptures'
thread_num = 3
save_roots = ['C:/GTA5_Data', 'C:/GTA5_Data', 'C:/GTA5_Data']

# when file count > save_num, extract data from those log files
save_num = 15
totalSaveCount = 0


def safeClose(event):
  global isActive
  isActive = False


if __name__ == '__main__':
  keyboard.on_release_key('q', safeClose)
  dataThreads = list()

  filesForThread = int(save_num/thread_num)+1

  for saveDir in save_roots:
    if not os.path.exists(saveDir):
      os.makedirs(saveDir)

  while isActive:
    curFileCount = 0
    currFileList = os.listdir(log_file_root)
    for fineName in currFileList:
      if fineName[-4:] == '.rdc':
        curFileCount += 1

    startT = time.time()
    if curFileCount > save_num:
      dataThreads.clear()
      for idx in range(thread_num):
        start_idx = filesForThread*idx
        end_idx = min(filesForThread*(idx+1), save_num)

        dataThreads.append(GTA5DataThread(str(idx), log_file_root))

        dataThreads[idx].setFileList(currFileList[start_idx:end_idx])
        dataThreads[idx].setSaveDir(save_roots[idx])

        dataThreads[idx].start()
        print('Thread[%d] start..'%idx)

      for idx in range(thread_num):
        dataThreads[idx].join()
      print('Thread finish processing')

      tempCount = 0
      for idx in range(thread_num):
        tempCount += dataThreads[idx].getSaveCount()

      print('Processing time: %f'%((time.time() - startT)/tempCount))

      totalSaveCount += tempCount
      print('Total save count: %d'%totalSaveCount)

    else:
      print('Curr file count: %s (press q to quit)'%curFileCount)
      time.sleep(1)

  print('quit data procesing..')
  keyboard.unhook_all()

