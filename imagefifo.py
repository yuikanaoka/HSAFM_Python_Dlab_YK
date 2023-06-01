#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Uchihashi
#
# Created:     23/02/2018
# Copyright:   (c) Uchihashi 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from filelist import FileList

import config
import struct
import numpy as np
import imagedisplay as ImD

class FileImport:
    def __init__(self, row):

        self.row = row


    def getheader(self):
        #print (config.files)
        print ("row")
        print (config.row)

        with open(config.files[self.row], "rb") as f:
            config.FileType = struct.unpack('i', f.read(4)) [0]
            print("FileType=" + str(config.FileType))   
            #config.FileType = struct.unpack('l', f.read(4)) [0]
            reserved=""
            if config.FileType == 1:
                config.FileHeaderSize = struct.unpack('i', f.read(4)) [0]
                config.FrameHeaderSize = struct.unpack('i', f.read(4)) [0]
                config.TextEncoding = struct.unpack('i', f.read(4)) [0]
                config.OpeNameSize = struct.unpack('i', f.read(4)) [0]

                config.CommentSize = struct.unpack('i', f.read(4)) [0]
                #print("commentsize=" + str(config.CommentSize))
                config.DataType1ch = struct.unpack('i', f.read(4)) [0]
                #print("DataType1ch=" + str(config.DataType1ch))
                config.DataType2ch = struct.unpack('i', f.read(4)) [0]
                #print("DataType2ch=" +str(config.DataType2ch))
                config.FrameNum = struct.unpack('i', f.read(4)) [0]
                #print("FrameNum=" +str(config.FrameNum))
                config.ImageNum = struct.unpack('i', f.read(4)) [0]
                #print("ImageNum=" +str(config.ImageNum))
                config.ScanDirection = struct.unpack('i', f.read(4)) [0]
                #print("ScanDirection=" +str(config.ScanDirection))
                config.ScanTryNum = struct.unpack('i', f.read(4)) [0]
                #print("ScanTryNum=" +str(config.ScanTryNum))
                config.XPixel = struct.unpack('i', f.read(4)) [0]
                print("XPixel=" +str(config.XPixel))
                config.YPixel = struct.unpack('i', f.read(4)) [0]
                print("YPixel=" +str(config.YPixel))
                config.XScanSize = struct.unpack('i', f.read(4)) [0]
                #print("XScanSize=" +str(config.XScanSize))
                config.YScanSize = struct.unpack('i', f.read(4)) [0]
                #print("YScanSize=" +str(config.YScanSize))
                config.AveFlag = struct.unpack('B', f.read(1)) [0]
                #print("AveFlag =" +str(config.AveFlag ))
                config.AveNum = struct.unpack('i', f.read(4)) [0]
                #print("AveNum=" +str(config.AveNum))
                config.Year = struct.unpack('i', f.read(4)) [0]
                #print("Year=" +str(config.Year))
                config.Month = struct.unpack('i', f.read(4)) [0]
                #print("Month=" +str(config.Month))
                config.Day = struct.unpack('i', f.read(4)) [0]
                #print("Day=" +str(config.Day))
                config.Hour = struct.unpack('i', f.read(4)) [0]
                #print("Hour=" +str(config.Hour))
                config.Minute = struct.unpack('i', f.read(4)) [0]
                #print("Minute=" +str(config.Minute))
                config.Second = struct.unpack('i', f.read(4)) [0]
                #print("Second=" +str(config.Second))
                config.XRound = struct.unpack('i', f.read(4)) [0]
                #print("XRound=" +str(config.XRound))
                config.YRound = struct.unpack('i', f.read(4)) [0]
                #print("YRound=" +str(config.YRound))
                config.FrameTime = struct.unpack('f', f.read(4)) [0]
                #print("FrameTime=" +str(config.FrameTime))
                config.Sensitivity = struct.unpack('f', f.read(4)) [0]
                #print("Sensitivity=" +str(config.Sensitivity))
                config.PhaseSens = struct.unpack('f', f.read(4)) [0]
                #print("PhaseSens=" +str(config.PhaseSens))
                config.Offset = struct.unpack('i', f.read(4)) [0]
                config.Offset = struct.unpack('i', f.read(4)) [0]
                config.Offset = struct.unpack('i', f.read(4)) [0]
                config.Offset = struct.unpack('i', f.read(4)) [0]
                config.MachineNo = struct.unpack('i', f.read(4)) [0]
                #print("MachineNo=" +str(config.MachineNo))
                config.ADRange = struct.unpack('i', f.read(4)) [0]
                #print("ADRange=" +str(config.ADRange))
                config.ADResolution = struct.unpack('i', f.read(4)) [0]
                #print("ADResolution=" +str(config.ADResolution))
                config.MaxScanSizeX = struct.unpack('f', f.read(4)) [0]
                #print("MaxScanSizeX=" +str(config.MaxScanSizeX))
                config.MaxScanSizeY = struct.unpack('f', f.read(4)) [0]
                #print("MaxScanSizeY=" +str(config.MaxScanSizeY))
                config.PiezoConstX = struct.unpack('f', f.read(4)) [0]
                #print("PiezoConstX=" +str(config.PiezoConstX))
                config.PiezoConstY = struct.unpack('f', f.read(4)) [0]
                #print("PiezoConstY=" +str(config.PiezoConstY))
                config.PiezoConstZ = struct.unpack('f', f.read(4)) [0]
                print("PiezoConstZ=" +str(config.PiezoConstZ))
                config.DriverGainZ = struct.unpack('f', f.read(4)) [0]
                print("DriverGainZ=" +str(config.DriverGainZ))
                f.seek(config.FileHeaderSize-config.CommentSize-config.OpeNameSize)
                #config.OpeName = ""
                #for line in range(1,10):
                data = f.read(config.OpeNameSize)
                config.OpeName= data.decode("UTF-8")
                #print("OpeName=" +config.OpeName)
                data =f.read(config.CommentSize)
                try:
                    config.Comment = data.decode("UTF-8")
                except  UnicodeDecodeError:
                    config.Comment=data.decode("shift_jis")

                #print("Comment=" +str(config.Comment))
            f.close()

    def OpenImage(self, fname):
        #print(fname)
        if(config.FrameNum == 0):
            return 0
        else:
            with open(fname, "rb") as f:
                f.seek(config.FileHeaderSize+(config.FrameHeaderSize+2*config.XPixel*config.YPixel)*config.index)

                config.CurrentNum = struct.unpack('I', f.read(4)) [0]
                #print("CurrentNum=" +str(config.CurrentNum))

                config.MaxData = struct.unpack('H', f.read(2)) [0]
                print("MaxData=" +str(config.MaxData))

                config.MiniData = struct.unpack('H', f.read(2)) [0]
                print("MiniData=" +str(config.MiniData))

                config.XOffset = struct.unpack('h', f.read(2)) [0]
                #print("XOffset=" +str(config.XOffset))

                config.YOffset = struct.unpack('h', f.read(2)) [0]
                #print("YOffset=" +str(config.YOffset))

                config.XTilt = struct.unpack('f', f.read(4)) [0]
                #print("XTilt=" +str(config.XTilt))

                config.YTilt = struct.unpack('f', f.read(4)) [0]
                #print("XTilt=" +str(config.XTilt))

                config.LaserFlag = struct.unpack('B', f.read(1)) [0]
                #print("LaserFlag=" +str(config.LaserFlag))

                f.seek(11,1)

                ary = np.fromfile(f, dtype="uint16", count=config.XPixel*config.YPixel) #read binaridata ndarray
                
                f.close()

            ary=np.reshape(ary, (config.YPixel, config.XPixel)) #convert to 2d matrix
            
            #config.aryData = np.resize(config.aryData, (config.YPixel, config.XPixel))
            config.RawaryData = np.resize(config.ZaryData, (config.YPixel, config.XPixel))
            #config.aryData = ary.astype(np.float64)
            config.RawaryData= ary.astype(np.float64)            
            #print(config.ZaryData[0][0])
            #print(config.ZaryData.shape)

            #config.aryData = (5.0-((config.aryData*10.0)/4096.0))*config.PiezoConstZ*config.DriverGainZ
            #config.aryData = 5.0-config.aryData*10.0*config.PiezoConstZ*config.DriverGainZ/4096.0
            config.RawaryData = (5.0-((config.RawaryData*10.0)/4096.0))*config.PiezoConstZ*config.DriverGainZ

            config.ZaryData = np.array(config.RawaryData)

            #print(config.DriverGainZ)
            #print(config.PiezoConstZ)

            #print(config.ZaryData.shape)
            #print(config.ZaryData[0][0])
            #print(config.aryData[0])
            #config.aryData = ary.astype(dtype = np.unit8)

            #if(frame == 0):
            #    ImD.imgdata = plt.imshow(np.uint8(config.aryData), cmap = 'gray', vmin=0, vmax=255, interpolation="nearest")
            #    plt.axis("off")
            #    plt.show()

            #imgdata = plt.imshow(np.uint8(config.aryData), cmap = 'gray', vmin=0, vmax=255, interpolation="nearest")

            disp = ImD.ImageDisplay()

            #check.TestAryf(aryf)
            disp.DispAryData()


def main():
    pass

if __name__ == '__main__':
    main()


            #cv2.imshow()
