# -------------------------------------------------------------------------------
# Name:        Line Profile
# Purpose:
#
# Author:      Uchihashi
#
# Created:     01/03/2018
# Last Edited: 05/04/2021 by shaoma
# Copyright:   (c) Uchihashi 2018
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import config
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (QWidget, QApplication, QPushButton, QLineEdit,
                             QHBoxLayout, QVBoxLayout, QTextEdit, QProgressBar,
                             QFileDialog, QListView, QAbstractItemView, QComboBox,
                             QDialog, QGridLayout, QHBoxLayout, QHeaderView, QLabel,
                             QProgressDialog, QPushButton, QSizePolicy, QTableWidget,
                             QTableWidgetItem, QSlider, QSpinBox, QToolButton, QStyle,
                             QCheckBox, QGroupBox, QBoxLayout, QMessageBox, QAction,
                             QFileDialog, QMainWindow, QMessageBox, QTextEdit, QMenu, QFrame, )
from PyQt5 import QtCore  # conda install pyqt
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from  matplotlib.figure import Figure
import numpy as np
import cv2
import matplotlib.pyplot as plt
import sys
import random
import math
import time

#plt.ion()
class LineWindow(QMainWindow):

    def __init__(self, parent=None):
        super(LineWindow, self).__init__(parent)
    


    
    


class LineProfile:

    def __init__(self):
       
       
        self.sx=0
        self.sy=int(config.dspimg.shape[0] / 2)
        self.ex=int(config.dspimg.shape[1])
        self.ey=int(config.dspimg.shape[0] / 2)
        self.plot=False
        
       
        self.colorarray=config.dspimg #colored img array
        self.grayarray=cv2.cvtColor(config.dspimg, cv2.COLOR_BGR2GRAY) #gray scale img array from 0 to 255 value
        self.zarray=config.ZaryData
        self.xscansize=config.XScanSize
        self.yscansize=config.YScanSize
        self.xpixel=config.XPixel
        self.ypixel=config.YPixel
        
        self.sxnm=0
        self.synm=0
        self.exnm=0
        self.eynm=0

        self.index=config.index
       
        self.s0=False #click event
        self.s1=False #drag and draw line event
        self.s2=False #drag and update lineprofile event
        self.s3=False #relase event


    def CloseEvent(self,event):
        config.lineopen=False
        config.lineclose=True
        
        print("line close event fired")
        
        print("line close"+str(config.lineclose))
        print("line open"+str(config.lineopen))
       
    def DrawLine(self,event, x, y, flags, param):
        
        
      
        if config.lineopen==True and config.lineclose==False:
            
            if event == cv2.EVENT_LBUTTONDOWN:  #左クリック押下時
                imageH = self.zarray.shape[0]
                imageW = self.zarray.shape[1]
                print("drawline "+str(self.index))
                self.s0 = True
                self.sx = x      #始点x
                self.sy = y      #始点y
                self.P1 = (x,y)
                self.height_startpoint=self.zarray[self.sy,self.sx]

            
                print("Left-clicked. Start point:(%d, %d)" %(self.sx, self.sy))
                
                
                self.sxnm=(self.sx/self.zarray.shape[1])*self.xscansize
                self.synm=(self.sy/self.zarray.shape[0])*self.yscansize
               
                    
            elif event == cv2.EVENT_MOUSEMOVE and self.s0 and (not self.s1):  #左クリックでドラッグ中
                self.ex = x
                self.ey = y
                self.P2 = (x,y)
                self.temp=config.dspimg.copy()
                cv2.line(self.temp,(self.sx,self.sy),(self.ex,self.ey),(0,255,0),2)
                cv2.imshow('img1ch', self.temp)
                self.s1 = True
                cv2.waitKey(1)
                self.s1 = False

                self.Calculate_Distance()

                dX = self.ex-self.sx
                dY = self.ey-self.sy
                dXa = np.abs(dX)
                dYa = np.abs(dY)

               
                distancelist = np.empty(shape=(np.maximum(dYa, dXa),3),dtype=np.float32)
                distancelist.fill(np.nan)

                negativeY = self.sy > self.ey
                negativeX = self.sx > self.ex

                if self.sx == self.ex and self.sy != self.ey: # vertical line
                    distancelist[:,0] = self.sx
                    if negativeY:
                        distancelist[:,1] = np.arange(self.sy-1, self.sy-dYa-1, -1)
                    else:
                        distancelist[:,1] = np.arange(self.sy+1, self.sy+dYa+1)
                elif self.sy == self.ey and self.sx != self.ex: # horizontal line
                    distancelist[:,1] = self.sy
                    if negativeX:
                        distancelist[:,0] = np.arange(self.sx-1, self.sx-dXa-1, -1)
                    else:
                        distancelist[:,0] = np.arange(self.sx+1, self.sx+dXa+1)
                elif self.sx == self.ex and self.sy == self.ey:
                    pass
                else:
                    steepSlope = dYa > dXa
                    if steepSlope:
                        slope_f32 = np.float32(dX)/np.float32(dY)
                        if negativeY:
                            distancelist[:,1] = np.arange(self.sy-1, self.sy-dYa-1, -1)
                        else:
                            distancelist[:,1] = np.arange(self.sy+1, self.sy+dYa+1)
                        distancelist[:,0] = (slope_f32*(distancelist[:,1]-self.sy)).astype(np.int)+self.sx
                    
                    else:
                        slope_f32 = np.float32(dY)/np.float32(dX)
                        if negativeX:
                            distancelist[:,0] = np.arange(self.sx-1, self.sx-dXa-1, -1)
                        else:
                            distancelist[:,0] = np.arange(self.sx+1, self.sx+dXa+1)
                        distancelist[:,1] = (slope_f32*(distancelist[:,0]-self.sx)).astype(np.int)+self.sy

                    colX = distancelist[:,0]
                    colY = distancelist[:,1]
                    distancelist = distancelist[(colX >=0) & (colY >= 0) & (colX < self.zarray.shape[1]) & (colY < self.zarray.shape[0])]
                    distancelist[:,2] = self.zarray[config.dspsize[1]-distancelist[:,1].astype(np.uint),distancelist[:,0].astype(np.uint)]
                    distancelist[:,2] = distancelist[:,2]-distancelist[:,2].min()
                    step=self.distance/len(distancelist[:,2])
                    distance_ticks= np.arange(len(distancelist[:,2]))*step
                    self.UpdatePlot(config.linewindow,config.figure,config.axes,distance_ticks, distancelist)

                self.s2 = True
                        
            
            elif event == cv2.EVENT_LBUTTONUP: #clear the state
                self.s2=False
                self.s1=False
                self.s0=False             
                print("Left-releasec. End point:(%d, %d)" %(self.ex, self.ey))
                

               

    def UpdatePlot(self,profile_window,profile_figure,profile_axes,distance_ticks,profile_zvaluelist):
        self.zvaluelist=profile_zvaluelist[:,2]
        self.line=profile_window
        self.figure=profile_figure
        self.axes=profile_axes

        self.line.set_data(distance_ticks,self.zvaluelist)
        self.axes.set_xlim(distance_ticks.min(),distance_ticks.max()) 
        self.axes.set_ylim(self.zvaluelist.min(),self.zvaluelist.max())
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        self.figure.canvas.mpl_connect("close_event",self.CloseEvent)
    
  
        
    
    def MakeProfileWindow(self):
        plt.ion()
        self.figure,self.axes= plt.subplots(figsize=(8,6))
        self.fnum=plt.figure(1)
        self.figure.canvas.set_window_title("Line Profile")
        self.line=self.axes.plot([],[])[0]
        config.linewindow=self.line
        config.figure=self.figure
        self.axes.set_xlabel("nm")
        config.axes=self.axes
        self.figure.canvas.mpl_connect("close_event",self.CloseEvent)
    
   

    def MouseSet(self,input_img_name):
        self.input_img_name=input_img_name
        cv2.setMouseCallback(self.input_img_name, self.DrawLine, None)

    def Calculate_Distance(self):
        self.height_endpoint=self.zarray[self.ey,self.ex]               
        self.exnm=(self.ex/self.zarray.shape[1])*self.xscansize
        self.eynm=(self.ey/self.zarray.shape[0])*self.yscansize
        self.distance=int(np.sqrt((self.exnm - self.sxnm) ** 2 + (self.eynm - self.synm) ** 2))
