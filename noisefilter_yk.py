# -------------------------------------------------------------------------------
# Name:        noisegfilter.py
# Purpose:
#
# Author:      Uchihashi
#
# Created:     27/02/2018
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
                             QFileDialog, QMainWindow, QMessageBox, QTextEdit, QMenu, QFrame, QRadioButton, QDoubleSpinBox)
from PyQt5 import QtCore  # conda install pyqt
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from  matplotlib.figure import Figure
from scipy import ndimage
from scipy.signal import wiener

import config
import numpy as np
import cv2
import matplotlib.pyplot as plt
import sys
import random
import math

import imagedisplay as ImD

from config import noisefilterpanel

class NoisefilterWindow(QtWidgets.QWidget):

    def __init__(self,parent=None):

        super(NoisefilterWindow, self).__init__(parent)
        
        #self.left = 300
        #self.top = 300
        #self.width = 300
        #self.height = 400

        if config.DispState  == 0:
            return 
        
        self.setGeometry(noisefilterpanel.left, noisefilterpanel.top, noisefilterpanel.width, noisefilterpanel.height)

        self.setWindowTitle("Noise Filters")

        top =10
        left = 30

        # Checkbox widget
        self.all_checkbox = QCheckBox("Auto", self)
        self.all_checkbox.setGeometry(QtCore.QRect(left, top, 100, 30))
        #self.params = NFilerParams() # initialize with default values
        self.all_checkbox.setChecked(config.noisefilter_auto)  # all_Filterに依存して初期値を設定
        self.all_checkbox.stateChanged.connect(self.on_all_checkbox_changed)

        top += 40

        # Selector widget
        self.selector_label = QLabel("Filter type:", self)
        self.selector_label.setGeometry(QtCore.QRect(left, top, 100, 30))
        self.selector = QComboBox(self)
        self.selector.setGeometry(QtCore.QRect(left+110, top, 120, 30))
        self.selector.addItems(["Average", "Gaussian", "Median", "Bilateral", "Destripe"])
        self.selector.setCurrentText(config.noisefilter_type)  # filter_typeに応じて初期値を設定
        self.selector.currentTextChanged.connect(self.update_filter_type)
        


        top += 40

        # Filter kernel size input widget
        self.kernel_size_label = QLabel("Filter kernel size (N x N):", self)
        self.kernel_size_label.setGeometry(QtCore.QRect(left, top, 150, 30))
        self.kernel_size_spinbox = QSpinBox(self)
        self.kernel_size_spinbox.setGeometry(QtCore.QRect(left+170, top, 50, 30))
        self.kernel_size_spinbox.setMinimum(3)
        self.kernel_size_spinbox.setMaximum(15)
        self.kernel_size_spinbox.setSingleStep(2)
        self.kernel_size_spinbox.setValue(config.kernel_size)  # kernel_sizeに応じて初期値を設定
        self.kernel_size_spinbox.valueChanged.connect(self.update_kernek_size)
       
        top += 40

        # Sigma X input widget
        self.sigma_x_label = QLabel("Sigma X:", self)
        self.sigma_x_label.setGeometry(QtCore.QRect(left, top, 100, 30))
        self.sigma_x_spinbox = QDoubleSpinBox(self)
        self.sigma_x_spinbox.setGeometry(QtCore.QRect(left+110, top, 120, 30))
        self.sigma_x_spinbox.setMinimum(0.1)
        self.sigma_x_spinbox.setMaximum(10)
        self.sigma_x_spinbox.setDecimals(1)
        self.sigma_x_spinbox.setSingleStep(0.1)
        self.sigma_x_spinbox.setValue(config.sigma_x)
        self.sigma_x_spinbox.valueChanged.connect(self.update_gaussian_sigma)
        

        # Sigma Y input widget
        self.sigma_y_label = QLabel("Sigma Y:", self)
        self.sigma_y_label.setGeometry(QtCore.QRect(left, top+40, 100, 30))
        self.sigma_y_spinbox = QDoubleSpinBox(self)
        self.sigma_y_spinbox.setGeometry(QtCore.QRect(left+110, top+40, 120, 30))
        self.sigma_y_spinbox.setMinimum(0.1)
        self.sigma_y_spinbox.setMaximum(10)
        self.sigma_y_spinbox.setDecimals(1)
        self.sigma_y_spinbox.setSingleStep(0.1)
        self.sigma_y_spinbox.setValue(config.sigma_y)
        self.sigma_y_spinbox.valueChanged.connect(self.update_gaussian_sigma)

         # d widget for Bilateral filter
        self.d_label = QLabel("d :", self)
        self.d_label.setGeometry(QtCore.QRect(left, top, 150, 30))
        self.d_spinbox = QSpinBox(self)
        self.d_spinbox.setGeometry(QtCore.QRect(left+170, top, 80, 30))
        self.d_spinbox.setMinimum(1)
        self.d_spinbox.setMaximum(50)
        self.d_spinbox.setValue(1)
        self.d_spinbox.setSingleStep(1)
        self.d_spinbox.valueChanged.connect(self.update_bilateral_filter)

        top += 40
    
        # sigmaColor widget for Bilateral filter
        self.sigma_color_label = QLabel("Sigma Color :", self)
        self.sigma_color_label.setGeometry(QtCore.QRect(left, top, 150, 30))
        self.sigma_color_spinbox = QDoubleSpinBox(self)
        self.sigma_color_spinbox.setGeometry(QtCore.QRect(left+170, top, 80, 30))
        self.sigma_color_spinbox.setMinimum(1)
        self.sigma_color_spinbox.setMaximum(100)
        self.sigma_color_spinbox.setSingleStep(1)
        self.sigma_color_spinbox.setValue(10)
        self.sigma_color_spinbox.valueChanged.connect(self.update_bilateral_filter)

        top += 40
    
        # sigmaSpace widget for Bilateral filter
        self.sigma_space_label = QLabel("Sigma Space :", self)
        self.sigma_space_label.setGeometry(QtCore.QRect(left, top, 150, 30))
        self.sigma_space_spinbox = QDoubleSpinBox(self)
        self.sigma_space_spinbox.setGeometry(QtCore.QRect(left+170, top, 80, 30))
        self.sigma_space_spinbox.setMinimum(1)
        self.sigma_space_spinbox.setMaximum(300)
        self.sigma_space_spinbox.setSingleStep(1)
        self.sigma_space_spinbox.setValue(10)
        self.sigma_space_spinbox.valueChanged.connect(self.update_bilateral_filter)
        self.sigma_space_label.hide()
        self.sigma_space_spinbox.hide()


        if  config.noisefilter_type == "Gaussian":
            self.sigma_x_label.show()
            self.sigma_x_spinbox.show()
            self.sigma_y_label.show()
            self.sigma_y_spinbox.show()
        else:
            self.sigma_x_label.hide()
            self.sigma_x_spinbox.hide()
            self.sigma_y_label.hide()
            self.sigma_y_spinbox.hide()

        if  config.noisefilter_type == "Bilateral":
            self.d_label.show()
            self.d_spinbox.show()
            self.sigma_color_label.show()
            self.sigma_color_spinbox.show()
            self.sigma_space_label.show()
            self.sigma_space_spinbox.show()                
        else:
            self.d_label.hide()
            self.d_spinbox.hide()
            self.sigma_color_label.hide()
            self.sigma_color_spinbox.hide()
            self.sigma_space_label.hide()
            self.sigma_space_spinbox.hide()

        if config.noisefilter_auto ==1 :
               
             self.update_image()
    
    def update_bilateral_filter(self):
        
        config.d = self.d_spinbox.value()
        config.sigma_color = self.sigma_color_spinbox.value()
        config.sigma_space = self.sigma_space_spinbox.value()

        if config.noisefilter_auto == 1 :
               
             self.update_image()

    def update_gaussian_sigma(self):

        config.sigma_x = self.sigma_x_spinbox.value()
        config.sigma_y = self.sigma_y_spinbox.value()
        
        if config.noisefilter_auto == 1 :
               
             self.update_image()

    def on_all_checkbox_changed(self, state):    
        
        if state == Qt.Checked:
            
            config.noisefilter_auto = 1

             
            self.update_image()
  
        else:
            
            config.noisefilter_auto = 0

            config.ZaryData = np.array(config.RawaryData)

        disp = ImD.ImageDisplay()
        disp.DispAryData()
    

    def update_kernek_size(self):

        config.kernel_size = self.kernel_size_spinbox.value()

        # 偶数値であれば、1を引いた値を使用する
        if config.kernel_size % 2 == 0:
            config.kernel_size -= 1

        if config.noisefilter_auto ==1 :
            self.update_image()

    def update_filter_type(self):

        config.noisefilter_type = self.selector.currentText()

        if  config.noisefilter_type == "Gaussian":
            self.sigma_x_label.show()
            self.sigma_x_spinbox.show()
            self.sigma_y_label.show()
            self.sigma_y_spinbox.show()
        else:
            self.sigma_x_label.hide()
            self.sigma_x_spinbox.hide()
            self.sigma_y_label.hide()
            self.sigma_y_spinbox.hide()

        if  config.noisefilter_type == "Bilateral":
            self.d_label.show()
            self.d_spinbox.show()
            self.sigma_color_label.show()
            self.sigma_color_spinbox.show()
            self.sigma_space_label.show()
            self.sigma_space_spinbox.show()                
        else:
            self.d_label.hide()
            self.d_spinbox.hide()
            self.sigma_color_label.hide()
            self.sigma_color_spinbox.hide()
            self.sigma_space_label.hide()
            self.sigma_space_spinbox.hide()

        if config.noisefilter_auto  ==1 :
               
             self.update_image()


    # def update_image(self):
         
    #     config.filter_type = self.selector.currentText()
        

    #     if config.filter_type == "Average":
    #         config.kernel_size = self.kernel_size_spinbox.value()  
    #         config.ZaryData = cv2.blur(config.RawaryData, ksize=(config.kernel_size , config.kernel_size ))  

    #     elif config.filter_type == "Gaussian":
    #         config.sigma_x = self.sigma_x_spinbox.value()
    #         config.sigma_y = self.sigma_y_spinbox.value()
    #         config.kernel_size = self.kernel_size_spinbox.value()      
    #         config.ZaryData = cv2.GaussianBlur(config.RawaryData, ksize=(config.kernel_size , config.kernel_size ), sigmaX=config.sigma_x, sigmaY=config.sigma_y)


    #     elif config.filter_type == "Median":
    #         config.kernel_size = self.kernel_size_spinbox.value()     

    #         arydata_float32 = config.RawaryData.astype(np.float32)
    #         config.ZaryData = ndimage.median_filter(arydata_float32, size=config.kernel_size)
        
    #     elif config.filter_type == "Bilateral":
    #         config.sigma_d = self.d_spinbox.value()
    #         config.sigma_color = self.sigma_color_spinbox.value()
    #         config.sigma_space = self.sigma_space_spinbox.value()
            
    #         # データを0から255の範囲に正規化して、uint8形式にキャスト
    #         min_val = config.RawaryData.min()
    #         max_val = config.RawaryData.max()
    #         arydata_uint8 = (((config.RawaryData - min_val) / (max_val - min_val)) * 255).astype(np.uint8)

    #         # バイラテラルフィルターを適用
    #         filtered_arydata_uint8 = cv2.bilateralFilter(arydata_uint8,  d=config.sigma_d, sigmaColor=config.sigma_color, sigmaSpace=config.sigma_space)

    #         # uint8形式のデータを元の範囲（float32）に戻す
    #         config.ZaryData = (filtered_arydata_uint8.astype(np.float32) / 255) * (max_val - min_val) + min_val
        
    #     disp = ImD.ImageDisplay()
    #     disp.DispAryData()
    
    def update_image(self):
         
        config.filter_type = self.selector.currentText()
        
        if config.filter_type == "Average":
            config.kernel_size = self.kernel_size_spinbox.value()  
         
        elif config.filter_type == "Gaussian":
            config.sigma_x = self.sigma_x_spinbox.value()
            config.sigma_y = self.sigma_y_spinbox.value()
            config.kernel_size = self.kernel_size_spinbox.value()      
           
        elif config.filter_type == "Median":
            config.kernel_size = self.kernel_size_spinbox.value()     

        elif config.filter_type == "Bilateral":
            config.sigma_d = self.d_spinbox.value()
            config.sigma_color = self.sigma_color_spinbox.value()
            config.sigma_space = self.sigma_space_spinbox.value()

        #AutoNoiseFilter()
        
        disp = ImD.ImageDisplay()
        disp.DispAryData()


def AutoNoiseFilter():
     
    if config.filter_type == "Average":
        
        config.ZaryData = cv2.blur(config.RawaryData, ksize=(config.kernel_size , config.kernel_size ))  
        
    elif config.filter_type == "Gaussian":
    
        config.ZaryData = cv2.GaussianBlur(config.RawaryData, ksize=(config.kernel_size , config.kernel_size ), sigmaX=config.sigma_x, sigmaY=config.sigma_y)

    elif config.filter_type == "Median":
        arydata_float32 = config.RawaryData.astype(np.float32)
        config.ZaryData = ndimage.median_filter(arydata_float32, size=config.kernel_size)
        
    elif config.filter_type == "Bilateral":
         # データを0から255の範囲に正規化して、uint8形式にキャスト
        min_val = config.RawaryData.min()
        max_val = config.RawaryData.max()
        arydata_uint8 = (((config.RawaryData - min_val) / (max_val - min_val)) * 255).astype(np.uint8)

        # バイラテラルフィルターを適用
        filtered_arydata_uint8 = cv2.bilateralFilter(arydata_uint8,  d=config.sigma_d, sigmaColor=config.sigma_color, sigmaSpace=config.sigma_space)

        # uint8形式のデータを元の範囲（float32）に戻す
        config.ZaryData = (filtered_arydata_uint8.astype(np.float32) / 255) * (max_val - min_val) + min_val
        
        #disp = ImD.ImageDisplay()
        #disp.DispAryData()

# def destripe_horizontal(image):
#     destriped_image = np.zeros_like(image.T)

#     # 水平ストライプノイズを除去するために、各列にWienerフィルターを適用
#     for i in range(image.T.shape[0]):
#         destriped_image[i, :] = wiener(image.T[i, :], mysize=5)  # mysizeはウィンドウサイズを指定します。適切な値に調整してください。

#     return destriped_image.T

    
    