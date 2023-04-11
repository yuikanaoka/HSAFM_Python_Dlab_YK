#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Uchihashi
#
# Created:     22/02/2018
# Copyright:   (c) Uchihashi 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import numpy as np
from PyQt5.QtWidgets import QApplication
import sys

class PanelSize:
    def __init__(self, width, height, left, top):
        self.width = width
        self.height = height
        self.left = left
        self.top = top


# information of desktop
app = QApplication(sys.argv)
screen = app.primaryScreen()
size = screen.size()
dspH = size.height()
dspW = size.width()

#  panel size definition
mainpanel = PanelSize(900, 400, 10, dspH-500)

# panels for image processing
backgroundpanel = PanelSize(300, 200, 10, dspH-500)
noisefilterpanel = PanelSize(400, 400, 10, dspH-500)
#Panelsize.mainpanel = Panelsize(mainpanel_width, mainpanel_height, mainpanel_left, mainpanel_top)

FileType = None
FileHeaderSize = None
FrameHeaderSize = None
TextEncoding = None
OpeNameSize  = None
CommentSize  = None
DataType1ch = None
DataType2ch = None
FrameNum = 500
XPixel = None
YPixel = None
XScanSize = None
YScanSize = None
FrameTime= float("nan")
PiezoConstX= float("nan")
PiezoConstY= float("nan")
PiezoConstZ= float("nan")
DriverGainZ= float("nan")
Offset = None
ADRange = None
ADResolution = None
AveFlag = None
AveNum = None
Year = None
Day = None
Hour = None
Minute = None
Second = None
XRound = None
YRound = None
MaxScanSizeX = float("nan")
MaxScanSizeY = float("nan")
FrameNum = None
MachineNo = None
ScanTryNum = None
Sensitivity = float("nan")
PhaseSens = float("nan")
ScanDirection = None
OpeName = ""
Comment = ""

CurrentNum = None
MaxData = None
MiniData = None
XOffset = None
YOffset  = None
XTilt  = None
YTilt = None
LaserFlag = None

files =[]
aryData = np.empty(0)
ZaryData=np.empty(0)
RawaryData=np.empty(0)

row=0

dspsize=1
dspimg =np.empty(0)

DIcolor = np.zeros((256, 1, 3), dtype=np.uint8)

FileNum =0
DispState = 0
DispMode = 1
pbSpeed = 1

# Remove bacgorund parameters
rb_plane_auto = 0
rb_plane_order = 1
rb_line_auto = 0
rb_line_order = 1
rb_line_type = 0
rb_line_direction = "Horizontal"
rb_histogram_slider_value = 0

# Noise Filter parameters
noisefilter_auto = 0
noisefilter_type = "Average"    
kernel_size = 3
sigma_x = 0.1
sigma_y = 0.1
sigma_d = 1 
sigma_space = 50
sigma_color = 75


lineclose=False
lineopen=False

linewindow=None
figure=None
axes=None

