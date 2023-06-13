# -------------------------------------------------------------------------------
# Name:        Line Profile
# Purpose:
#
# Author:      Uchihashi
#
# Created:     01/03/2018
# Last Edited: 06/13/2021 by shaoma
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
from matplotlib.widgets import CheckButtons, Button
from  matplotlib.figure import Figure
from matplotlib.lines import Line2D
import numpy as np
import cv2
import matplotlib.pyplot as plt
import sys
import math
from scipy.interpolate import interp2d
from matplotlib.widgets import Cursor

#plt.ion()
class LineWindow(QMainWindow):

    def __init__(self, parent=None):
        super(LineWindow, self).__init__(parent)
    
class LineProfile:

    def __init__(self):
       
        print ("config.dspimg.shape[0] is :"+str(config.dspimg.shape[0]))
        print ("config.dspimg.shape[1] is :"+str(config.dspimg.shape[1]))
        self.sx=0
        self.sy=int(config.dspimg.shape[0] / 2)
        self.ex=int(config.dspimg.shape[1])
        self.ey=int(config.dspimg.shape[0] / 2)
        self.LineList=np.empty((2,2),dtype=np.int16)
        self.pts = np.array([[self.sx,self.sy],[self.ex,self.ey]],np.int32)
        self.plot=False
        
       
        self.colorarray=config.dspimg #colored img array
        self.grayarray=cv2.cvtColor(config.dspimg, cv2.COLOR_BGR2GRAY) #gray scale img array from 0 to 255 value
        #need to 180° 左回転、左右対称に反転
        
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
        self.s3=False #relase event, line existence
        self.s4=False #set start point
        self.s5=False #set end point
        self.status = 0x00
        #self.index_list = index_list()


    def CloseEvent(self,event):
        config.lineopen=False
        config.lineclose=True
        
        print("line close event fired")
        
        print("line close"+str(config.lineclose))
        print("line open"+str(config.lineopen))
       
   # draw line between clicked point and fetch z-data along the line, plot z data on new window 
   # 1. detect mouse click event
   # 2a. check if line exists, if no, create line on mouse move
   # 2b. if yes, check if new click close to any existed point or line
   # 2b1. if close to any of the node, drage the node
   # 2b2. if not, create a new node
   # 3. get the pixel index along the line
   # 4. fetch the z-data from given pixel index
   # 5. put the z-data into plot
    def DrawLine(self,event, x, y, flags, param):
       
        if config.lineopen==True and config.lineclose==False:
            self.zarray=np.fliplr(np.rot90(config.ZaryData,2))
            
            if event == cv2.EVENT_LBUTTONDOWN:  #左クリック押下時
                #set_startpnt = False
                #set_endpnt = False
                # if self.s3:
                #     #status s3: released event, line exists
                #     #if line exsited, check distance between the clicked point and the line
                #     new_pts = [x,y]
                #     print("3rd pnt is :",new_pts)
                #     tmp_dist = calc_PLdist(new_pts,self.LineList)
                #     print("Min Dist is: ",tmp_dist.min())
                #     print("Max Dist is: ",tmp_dist.max())
                #     print("tmp_dist[0]:",tmp_dist[0])
                #     print("tmp_dist[-1]:",tmp_dist[-1])
                #     if tmp_dist.min()<detect_radius:
                #         if tmp_dist.min() in tmp_dist[0:int(0.10*len(tmp_dist))]:
                #             print("min at start point")
                #             #set_startpnt = True
                #             self.s4 = True
                #             self.s5 = False
                #             self.sx = x
                #             self.sy = y
                #             self.index_list.start_point = Node([x,y])
                #         elif tmp_dist.min() in tmp_dist[-1:-int(0.10*len(tmp_dist)):-1]:
                #             print("min at end point")
                #             #set_endpnt = True
                #             self.s5 = True
                #             self.s4 = False
                #             self.ex = x
                #             self.ey = y
                #             self.index_list.end_point = Node([x,y])
                #         else:
                #             print("we will add one point here")
                #             # fetch closest pixel coordinates in the line
                #             tmp_idx = np.where(tmp_dist == tmp_dist.min())[0]
                #             self.pts = np.insert([[self.sx,self.sy],[self.ex,self.ey]],1,[x,y],axis=0)
                #             print("points on line:",self.pts)
                #             print("tmp_idx: ", tmp_idx[0])
                #             tmp_idx = tmp_idx[0]
                #             tmp_x=self.LineList[tmp_idx,:]
                #             print("tmp_x:", tmp_x)
                #             print("point list:", self.pts.shape)
                #             cv2.circle(self.temp,(tmp_x[0],tmp_x[1]),5,(200,200,0),-1)
                #             cv2.imshow('img1ch', self.temp)
                #             cv2.waitKey(1)

                #     imageH = self.zarray.shape[0]
                #     imageW = self.zarray.shape[1]
                #     self.s0 = True
                #     self.sx = x      #始点x
                #     self.sy = y      #始点y
                #     self.index_list.start_point = Node([x,y])
                #     self.index_list.print_index()
                #     self.height_startpoint=self.zarray[self.sy,self.sx]
                # else:
                #     self.status = self.status or 0x01 
                #     imageH = self.zarray.shape[0]
                #     print ("imageH: ",imageH)
                #     imageW = self.zarray.shape[1]
                #     print ("imageW: ",imageW)
                #     print("drawline "+str(self.index))
                #     self.s0 = True
                #     self.s5 = True
                #     self.s4 = False
                #     self.sx = x      #始点x
                #     print("sx: ",self.sx)
                #     self.sy = y      #始点y
                #     print("sy: ",self.sy)
                #     self.index_list.start_point = Node([x,y])
                #     self.index_list.print_index()
                #     self.height_startpoint=self.zarray[self.sy,self.sx]
                self.s0 = True
                self.sx = x      #始点x
                self.sy = y      #始点y
                self.P1 = (x,y)
                print("Left-clicked. Start point:(%d, %d)" %(self.sx, self.sy))
                #temp_function(self.sx,self.sy)
                # self.sxori=int((self.sx*self.zarray.shape[1])/config.dspimg.shape[1])
                # self.syori=int((self.sy*self.zarray.shape[0])/config.dspimg.shape[0])
                
                # self.sxnm=(self.sxori/self.zarray.shape[1])*self.xscansize
                # self.synm=(self.syori/self.zarray.shape[0])*self.yscansize
               
                    
            elif event == cv2.EVENT_MOUSEMOVE and self.s0 and (not self.s1):  #左クリックでドラッグ中
                # if click around start point
                self.ex = x
                self.ey = y
                self.P2 = (x,y)
                self.temp=config.dspimg.copy()
                cv2.line(self.temp,(self.sx,self.sy),(self.ex,self.ey),(0,255,0),2)
                cv2.imshow('img1ch', self.temp)
                self.s1 = True
                cv2.waitKey(1)
                self.s1 = False

                #self.Calculate_Distance()

                
                # dislistlen=int(np.sqrt(dXa**2+dYa**2))
                # print("dislistlen: ", dislistlen)
                #dislistlen2=int(np.sqrt(((dX*self.zarray.shape[0])/config.dspimg.shape[0]))**2+((dY*self.zarray.shape[1])/config.dspimg.shape[1])**2)
                #print("dislistlen2: ", dislistlen2)

                #self.zarray=np.fliplr(np.rot90(self.zarray,2))

                self.exori=int((self.ex*self.zarray.shape[1])/config.dspimg.shape[1])
                self.eyori=int((self.ey*self.zarray.shape[0])/config.dspimg.shape[0])
                self.sxori=int((self.sx*self.zarray.shape[1])/config.dspimg.shape[1])
                self.syori=int((self.sy*self.zarray.shape[0])/config.dspimg.shape[0])

                print("exori: ",self.exori)
                print("eyori: ",self.eyori)
                print("sxori: ",self.sxori)
                print("syori: ",self.syori)
                
                
                

                dx = self.exori-self.sxori
                dy = self.eyori-self.syori
                print("dx: ",dx)
                print("dy: ",dy)
                line_length = int(math.sqrt(dx**2 + dy**2))
                #print("line_length: ",line_length)

                dxnm=dx*(config.XScanSize/config.XPixel)
                print("dxnm: ",dxnm)
                dynm=dy*(config.YScanSize/config.YPixel)
                print("dynm: ",dynm)
                line_length_nm=int(np.sqrt(dxnm**2+dynm**2))
                print("line_length_nm: ",line_length_nm)    
                
                dXa = np.abs(dx)
                dYa = np.abs(dy)

                dXa=int((dx*self.zarray.shape[0])/config.dspimg.shape[0])
                dYa=int((dy*self.zarray.shape[1])/config.dspimg.shape[1])

                 # Check if line exists (if origin and end are not the same point)
                if line_length > 0:
                    x_spacing = dx / line_length
                    y_spacing = dy / line_length

                    points = []
                    values = []

                    # Iterate over the line_length to get equally spaced points and corresponding values
                    for i in range(line_length + 1):
                        x = round(self.sxori + i * x_spacing)
                        y = round(self.syori + i * y_spacing)
                        points.append((x, y))
                        values.append(self.zarray[y][x])

                else:
                    # If origin and end are the same point, just use the single point
                    points = [(self.sxori, self.syori)]
                    values = [self.zarray[self.syori][self.sxori]]

                print("points: ",points)
                print("values: ",values)
                #print("line_length: ",len(values))

                scaling_factor = line_length_nm / line_length
                # Create a list of nm positions corresponding to values
                nm_positions = [i * scaling_factor for i in range(len(values))]
                print("nm_positions: ",len(nm_positions))

                config.nm_positions=nm_positions
                config.heightvalues=values



                self.UpdatePlot(nm_positions, values)

                self.s2 = True
                        
            
            elif event == cv2.EVENT_LBUTTONUP: #clear the state
                self.s2=False
                self.s1=False
                self.s0=False
                np.savetxt("zarray.csv",self.zarray)             
                print("Left-releasec. End point:(%d, %d)" %(self.ex, self.ey))
                

               

    def UpdatePlot(self,distance_ticks,profile_zvaluelist):
        self.zvaluelist=profile_zvaluelist
        #config.linewindow,config.figure,config.axes
        #self.line=profile_window
        # self.figure=profile_figure
        # self.axes=profile_axes

        config.linewindow.set_data(distance_ticks,self.zvaluelist)
        config.linewindow.set_color("red")
        #self.axes.set_xlim(max(distance_ticks),min(distance_ticks)) 
        config.axes.set_xlim(min(distance_ticks),max(distance_ticks)) 
        config.axes.set_ylim(min(self.zvaluelist),max(self.zvaluelist)+1)
        #plt.gca().invert_yaxis()
        config.figure.canvas.draw()
        config.figure.canvas.flush_events()
        config.figure.canvas.mpl_connect("close_event",self.CloseEvent)
    
    def MakeProfileData(self):
        self.dbg_echo()
        #wait to move lineprofile data calculation here
    
    def MakeProfileWindow(self):
        plt.ion()
        self.figure,self.axes= plt.subplots(figsize=(8,4))
        self.fnum=plt.figure(1)
        #self.figure.canvas.set_title("Line Profile")
        Multi_chk_pos = plt.axes([.12, .85, .1, .15]) # (x1,y1,x2,y2): make checkbox at (x1,y1) with a size of (x2,y2)
        Multi_chk_pos.set_axis_off() # turn off the surrounding line of checkbox
        Cursor_chk_pos = plt.axes([.25, .85, .10, .15])
        Cursor_chk_pos.set_axis_off()
        #self.Multipnt_chk = CheckButtons(Multi_chk_pos,['Multi-Point'])
        self.Cursor_chk = CheckButtons(Cursor_chk_pos,['Cursor']) # default status is False
        self.cursor1=None
        self.cursor2=None
        self.Cursor_chk.on_clicked(self.Cursor_chk_func)
        axReset = plt.axes([0.38, 0.9, 0.1, 0.05])
        self.bnext = Button(axReset, 'Reset',color = "white")
        self.bnext.on_clicked(self.dbg_echo)
        self.bnext.on_clicked(self.reset_LineProfile)
        self.line=self.axes.plot([],[])[0]
        config.linewindow=self.line
        config.figure=self.figure
        self.axes.set_xlabel("nm")
        config.axes=self.axes
        self.figure.canvas.mpl_connect("close_event",self.CloseEvent)
    
   

    def MouseSet(self,input_img_name):
        self.input_img_name=input_img_name
        cv2.setMouseCallback(self.input_img_name, self.DrawLine, None)

    # Calculate_Distance function calculates the distance between start point and end point, unit in nm
    # The calculated distance, self.distance is for make linespan of lineprofile plot
    def Calculate_Distance(self):
        print("self.zarray.shape: ", self.zarray.shape[0], self.zarray.shape[1])
        self.exori=int((self.ex*self.zarray.shape[1])/config.dspimg.shape[1])
        self.eyori=int((self.ey*self.zarray.shape[0])/config.dspimg.shape[0])
        self.height_endpoint=self.zarray[self.eyori,self.exori]               
        self.exnm=(self.exori/self.zarray.shape[1])*self.xscansize
        self.eynm=(self.eyori/self.zarray.shape[0])*self.yscansize
        self.distance=int(np.sqrt((self.exnm - self.sxnm) ** 2 + (self.eynm - self.synm) ** 2))
    
    def pnt_line_dist(self,pts):
        old_line = [[self.sx, self.sy],[self.ex,self.ey]]
        tmp = old_line-pts
    
    #reset_LineProfile just remove the drawn line on image but keep the z data until new line drawn
    def reset_LineProfile(self,event):
        self.temp=config.dspimg.copy()
        cv2.imshow('img1ch', self.temp)
        cv2.waitKey(1)

    def dbg_echo(self,event):
        print("hello!")

    def point_insert(self):
        print("greetings")
    
    def Cursor_chk_func(self, label):
        cursor_checked = self.Cursor_chk.get_status()[0]

        if cursor_checked:
            print("Cursor_chk_func")

            # If cursor does not exist, create it
            if self.cursor1 is None:
                self.cursor1 = SnaptoCursor(config.axes, config.nm_positions, config.heightvalues)
                config.figure.canvas.mpl_connect('button_press_event', self.cursor1.onclick)

            # Show the dot and activate the cursor
            self.cursor1.set_visible(True)
            self.cursor1.activate()
        else:
            print("Cursor_chk_func else")

            # Hide the dot, deactivate the cursor, and clear the previous markers and legend
            if self.cursor1 is not None:
                self.cursor1.set_visible(False)
                self.cursor1.deactivate()
                self.cursor1.clear_markers()
                self.cursor1.clear_legend()

        config.figure.canvas.draw()
        config.figure.canvas.flush_events()
        config.figure.canvas.mpl_connect("close_event", self.CloseEvent)

from matplotlib.lines import Line2D
import numpy as np
from matplotlib.widgets import Cursor

class SnaptoCursor(Cursor):
    def __init__(self, ax, x, y, **kwargs):
        super().__init__(ax, **kwargs)
        self.x = x
        self.y = y
        self.dot, = ax.plot(0, 0, 'bo', markersize=10)
        self.dot.set_visible(False)
        self.markers = []  # list to store markers
        self.set_count = 0  # counter to track click sets
        self.active = False  # cursor is inactive by default

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def onmove(self, event):
        if not self.active:
            return
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            ind = np.argmin(np.hypot(x - self.x, y - self.y))
            self.dot.set_data(self.x[ind], self.y[ind])
            self._update()
            self.ax.figure.canvas.draw()

    def onclick(self, event):
        if not self.active:
            return
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            ind = np.argmin(np.hypot(x - self.x, y - self.y))
            color = 'green' if self.set_count % 2 == 0 else 'yellow'
            marker = self.ax.plot(self.x[ind], self.y[ind], 'o', color=color, markersize=10)[0]
            self.markers.append(marker)
            if self.set_count >= 1 and self.set_count % 2 != 0:
                # Remove markers and legend for the previous set
                for m in self.markers[:-2]:
                    m.remove()
                self.markers = self.markers[-2:]
                legend = self.ax.get_legend()
                if legend:
                    legend.remove()
            self.update_legend()
            self.ax.figure.canvas.draw()
            self.set_count += 1

    def set_visible(self, visible):
        self.dot.set_visible(visible)

    def update_legend(self):
        if len(self.markers) >= 2:
            legend_elements = []
            for i, marker in enumerate(self.markers[-2:]):
                x, y = marker.get_data()
                label = f'Click {self.set_count-1 if i == 0 else self.set_count}: x={x[0]}, y={y[0]}'
                legend_elements.append(Line2D([0], [0], marker='o', color='w', markerfacecolor=marker.get_color(), markersize=10, label=label))
            # Add legend for difference between the two clicks
            x1, y1 = self.markers[-2].get_data()
            x2, y2 = self.markers[-1].get_data()
            dx, dy = x2[0] - x1[0], y2[0] - y1[0]
            legend_elements.append(Line2D([0], [0], marker='o', color='w', label=f'Difference: dx={dx}, dy={dy}'))
            self.ax.legend(handles=legend_elements, bbox_to_anchor=(1, 1), loc='upper left', fontsize='small')

    def clear_legend(self):
        legend = self.ax.get_legend()
        if legend:
            legend.remove()

    def clear_markers(self):
        for m in self.markers:
            m.remove()
        self.markers = []  # Reset the markers list
        self.set_count = 0  # Reset the click count
