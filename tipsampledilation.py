# -------------------------------------------------------------------------------
# Name:        tipsampledilation.py
# Purpose:     for afm simulation
#
# Author:      Kanaoka
#
# Created:     09/05/2023
# 
# Licence:     <your licence>
# -------------------------------------------------------------------------------
import sys
import os
import math
import struct

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
from PyQt5.QtGui import QPixmap, QPainter, QPen, QImage
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LinearSegmentedColormap


import numpy as np
import time
import threading
import datetime

import cv2

import io

from filelist import FileList
from imagefifo import FileImport

from Bio.PDB import PDBParser
import pandas as pd
from PIL import Image


import config
import lineprofile as lp
import removebackground as rb
import noisefilter as nf

import dilationfunctionmodule
from concurrent.futures import ThreadPoolExecutor

class TipSampleDilationWindow(QMainWindow):

    def __init__(self):

        super().__init__()
        
        # result = config.get_savedparam("panel", "Tip Sample Dilation")
        # if result is not None:
        #   # 一致する行が見つかった場合は、resultを処理する
        #     config.panel_left, config.panel_top, config.panel_width, config.panel_height = result
        # else:
        config.panel_width=  1100
        config.panel_height = 800
        config.panel_top = 100
        config.panel_left = 100


        self.setGeometry(config.panel_left , config.panel_top , config.panel_width, config.panel_height) 

        self.setWindowTitle("Tip Sample Dilation")

        self.main_layout = QHBoxLayout()


        #=======================
        # set the left panel
        #=======================

        self.left_groupbox= QGroupBox("Set Parameter")
        self.left_groupbox.setFixedSize(500, 800)
        self.left_groupbox_layout = QVBoxLayout()

        #=======================
        #set the right panel
        #=======================
        self.right_groupbox= QGroupBox("Simulation")
        self.right_groupbox.setFixedSize(500, 800)
        self.right_groupbox_layout = QVBoxLayout()

        """
        for left panel
        """

        #=======================
        # Tip Geometry
        #=======================
        self.tipgeometry_layout = QHBoxLayout()
        self.tipgeometry = QGroupBox("Tip Geometry")
        self.tipgeometry.setFixedSize(450, 100)
        self.tipgeometry.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px

        #tip raidus
        self.tipradius_layout = QVBoxLayout()  # Create a new QVBoxLayout for the radius
        self.tipradius_label = QLabel("Tip Radius") 
        self.tipradius = QDoubleSpinBox()
        self.tipradius.setRange(1, 5)
        self.tipradius.setSingleStep(0.5)
        self.tipradius_layout.addWidget(self.tipradius_label)
        self.tipradius_layout.addWidget(self.tipradius)
        self.tipradius.valueChanged.connect(self.tipradius_change)

        #tip shape
        self.tipshape_layout = QVBoxLayout()  # Create a new QVBoxLayout for the shape
        self.tipshape_label = QLabel("Tip Shape")
        self.tipshape = QComboBox()
        self.tipshape.addItem("Cone")
        self.tipshape.addItem("Paraboloid")
        self.tipshape_layout.addWidget(self.tipshape_label)
        self.tipshape_layout.addWidget(self.tipshape)
        self.tipshape.currentIndexChanged.connect(self.tipshape_change)

        #pixel x direction
        self.pixelxdirection_layout = QVBoxLayout()  # Create a new QVBoxLayout for the shape
        self.pixelxdirection_label = QLabel("Pixel x direction")
        self.pixelxdirection = QSpinBox()
        self.pixelxdirection.setRange(50, 100)
        self.pixelxdirection.setSingleStep(1)
        self.pixelxdirection_layout.addWidget(self.pixelxdirection_label)
        self.pixelxdirection_layout.addWidget(self.pixelxdirection)
        self.pixelxdirection.valueChanged.connect(self.pixelxdirection_change)

        #tip angle
        self.tipangle_layout = QVBoxLayout()  # Create a new QVBoxLayout for the shape
        self.tipangle_label = QLabel("Tip Angle")
        self.tipangle = QSpinBox()
        self.tipangle.setRange(1, 100)
        self.tipangle.setSingleStep(1)
        self.tipangle.setValue(10)
        self.tipangle_layout.addWidget(self.tipangle_label)
        self.tipangle_layout.addWidget(self.tipangle)
        self.tipangle.valueChanged.connect(self.tipangle_change)



        # Add the layouts 
        self.tipgeometry_layout.addLayout(self.tipradius_layout)
        self.tipgeometry_layout.addLayout(self.tipshape_layout)
        self.tipgeometry_layout.addLayout(self.pixelxdirection_layout)
        self.tipgeometry_layout.addLayout(self.tipangle_layout)

        # Set the layout to the QGroupBox
        self.tipgeometry.setLayout(self.tipgeometry_layout)

        #=======================
        # Tip Position
        #=======================
        self.tipposition_layout = QVBoxLayout()
        self.tipposition = QGroupBox("Tip Geometry")
        self.tipposition.setFixedSize(450, 200)
        self.tipposition.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px

        #tip position x
        self.tipposition_x_layout = QVBoxLayout()  # Create a new QVBoxLayout for the tip postion
        self.tipposition_x_label_layout = QHBoxLayout() # Create a new QHBoxLayout for the tip postion label
        self.tipposition_x_label = QLabel("X position") 
        self.tipposition_x_value_label = QLabel() 
        self.tipposition_x = QSlider(Qt.Horizontal)
        self.tipposition_x.setRange(-100, 100)
        self.tipposition_x.setSingleStep(5)
        self.tipposition_x.setValue(0)
        self.tipposition_x_value_label.setText(str(self.tipposition_x.value()))  # Set the initial value
        self.tipposition_x.valueChanged.connect(self.update_tipposition_x_label)  # Connect the valueChanged signal to update_label
        # Add the widgets to the layout
        self.tipposition_x_label_layout.addWidget(self.tipposition_x_label)
        self.tipposition_x_label_layout.addWidget(self.tipposition_x_value_label)  # Add the value label to the layout
        # Add the label layout and slider to the main layout
        self.tipposition_x_layout.addLayout(self.tipposition_x_label_layout)  # Add the label layout to the main layout
        self.tipposition_x_layout.addWidget(self.tipposition_x)  # Add the slider to the main layout


        #tip position y
        self.tipposition_y_layout = QVBoxLayout()  # Create a new QVBoxLayout for the tip postion
        self.tipposition_y_label_layout = QHBoxLayout() # Create a new QHBoxLayout for the tip postion label
        self.tipposition_y_label = QLabel("Y position")
        self.tipposition_y_value_label = QLabel()
        self.tipposition_y = QSlider(Qt.Horizontal)
        self.tipposition_y.setRange(-100, 100)
        self.tipposition_y.setSingleStep(5)
        self.tipposition_y.setValue(0)
        self.tipposition_y_value_label.setText(str(self.tipposition_y.value()))  # Set the initial value
        self.tipposition_y.valueChanged.connect(self.update_tipposition_y_label)  # Connect the valueChanged signal to update_label
        # Add the widgets to the layout
        self.tipposition_y_label_layout.addWidget(self.tipposition_y_label)
        self.tipposition_y_label_layout.addWidget(self.tipposition_y_value_label)  # Add the value label to the layout
        # Add the label layout and slider to the main layout
        self.tipposition_y_layout.addLayout(self.tipposition_y_label_layout)  # Add the label layout to the main layout
        self.tipposition_y_layout.addWidget(self.tipposition_y)  # Add the slider to the main layout


        # tip position z
        self.tipposition_z_layout = QVBoxLayout()  # Create a new QVBoxLayout for the tip postion
        self.tipposition_z_label_layout = QHBoxLayout()  # Create a new QHBoxLayout for the tip postion label
        self.tipposition_z_label = QLabel("Z position")
        self.tipposition_z_value_label = QLabel()
        self.tipposition_z = QSlider(Qt.Horizontal)
        self.tipposition_z.setRange(-100, 100)
        self.tipposition_z.setSingleStep(5)
        self.tipposition_z.setValue(0)
        self.tipposition_z_value_label.setText(str(self.tipposition_z.value()))  # Set the initial value
        self.tipposition_z.valueChanged.connect(self.update_tipposition_z_label)  # Connect the valueChanged signal to update_label
        # Add the widgets to the layout
        self.tipposition_z_label_layout.addWidget(self.tipposition_z_label)
        self.tipposition_z_label_layout.addWidget(self.tipposition_z_value_label)  # Add the value label to the layout
        # Add the label layout and slider to the main layout
        self.tipposition_z_layout.addLayout(self.tipposition_z_label_layout)  # Add the label layout to the main layout
        self.tipposition_z_layout.addWidget(self.tipposition_z)  # Add the slider to the main layout


        #add the layout to the tip psoition layout
        self.tipposition_layout.addLayout(self.tipposition_x_layout)
        self.tipposition_layout.addLayout(self.tipposition_y_layout)
        self.tipposition_layout.addLayout(self.tipposition_z_layout)
        self.tipposition.setLayout(self.tipposition_layout)


        # =======================
        # Smaple Appearance
        # =======================
        self.sampleappearance_layout = QHBoxLayout()
        self.sampleappearance = QGroupBox("Sample Appearance")
        self.sampleappearance.setFixedSize(450, 100)
        self.sampleappearance.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px

        #sample atom
        self.sampleatom_layout = QVBoxLayout()  # Create a new QVBoxLayout for the tip postion
        self.sampleatom_label = QLabel("Atom")
        self.sampleatom = QComboBox()
        self.sampleatom.addItems(["C","N","O","ALL"])
        self.sampleatom_layout.addWidget(self.sampleatom_label)
        self.sampleatom_layout.addWidget(self.sampleatom)
        self.sampleatom.currentIndexChanged.connect(self.atomtype_change)  # Connect the valueChanged signal to update_label


        #sample appearance type
        self.sampleappearancetype_layout = QVBoxLayout()  # Create a new QVBoxLayout for the tip postion
        self.sampleappearancetype_label = QLabel("Appearance Type")
        self.sampleappearancetype = QComboBox()
        self.sampleappearancetype.addItems(["Dot","Sphere","Ribbon","Line"])
        self.sampleappearancetype_layout.addWidget(self.sampleappearancetype_label)
        self.sampleappearancetype_layout.addWidget(self.sampleappearancetype)


        #add the layout to the sample appearance layout
        self.sampleappearance_layout.addLayout(self.sampleatom_layout)
        self.sampleappearance_layout.addLayout(self.sampleappearancetype_layout)
        self.sampleappearance.setLayout(self.sampleappearance_layout)

        # =======================
        # Sample orientation
        # =======================
        self.sampleorientation_layout = QVBoxLayout()
        self.sampleorientation = QGroupBox("Sample Orientation")
        self.sampleorientation.setFixedSize(450, 300)
        self.sampleorientation.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
        
        #sample orientation x
        self.sampleorientation_x_layout = QVBoxLayout()  # Create a new QVBoxLayout for the tip postion
        self.sampleorientation_x_label = QLabel("X Axis")
        # Create a QDoubleSpinBox for the step size
        self.step_size_spinbox_x = QDoubleSpinBox()
        self.step_size_spinbox_x.setRange(1, 100)
        self.step_size_spinbox_x.setSingleStep(1)
        self.step_size_spinbox_x.setValue(1.0)
        self.step_size_spinbox_x.valueChanged.connect(self.update_step_size_x)  # Connect the valueChanged signal to update_label
        # Create a label to display the value
        self.button_increment = QPushButton('Increase')
        self.button_increment.clicked.connect(self.increment_value_x)
        self.button_decrement = QPushButton('Decrease')
        self.button_decrement.clicked.connect(self.decrement_value_x)
        # Initialize the value
        self.value = 0
        # Create a new horizontal layout for the buttons
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.step_size_spinbox_x)  # Add the spinbox to the layout
        self.buttons_layout.addWidget(self.button_increment)  # Add the increase button to the layout
        self.buttons_layout.addWidget(self.button_decrement)  # Add the decrease button to the layout
        # Add the buttons layout, label, and label to the sampleorientation_x_layout
        self.sampleorientation_x_layout.addWidget(self.sampleorientation_x_label)  # Add the label to the layout
        self.sampleorientation_x_layout.addLayout(self.buttons_layout)


        #sample orientation y
        self.sampleorientation_y_layout = QVBoxLayout()  # Create a new QVBoxLayout for the tip postion
        self.sampleorientation_y_label = QLabel("Y Axis")
        self.step_size_spinbox_y = QDoubleSpinBox()
        self.step_size_spinbox_y.setRange(1, 100)
        self.step_size_spinbox_y.setSingleStep(1)
        self.step_size_spinbox_y.setValue(1.0)
        self.step_size_spinbox_y.valueChanged.connect(self.update_step_size_y)
        # Create a label to display the value
        self.button_increment = QPushButton('Increase')
        self.button_increment.clicked.connect(self.increment_value_y)
        self.button_decrement = QPushButton('Decrease')
        self.button_decrement.clicked.connect(self.decrement_value_y)
        # Initialize the value
        self.value = 0
        #self.step_size = self.step_size_spinbox.value()
        # Create a new horizontal layout for the buttons
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.step_size_spinbox_y)  # Add the spinbox to the layout
        self.buttons_layout.addWidget(self.button_increment)  # Add the increase button to the layout
        self.buttons_layout.addWidget(self.button_decrement)  # Add the decrease button to the layout
        # Add the buttons layout, label, and label to the sampleorientation_x_layout
        self.sampleorientation_y_layout.addWidget(self.sampleorientation_y_label)  # Add the label to the layout
        self.sampleorientation_y_layout.addLayout(self.buttons_layout)


        #sample orientation z
        self.sampleorientation_z_layout = QVBoxLayout()  # Create a new QVBoxLayout for the tip postion
        self.sampleorientation_z_label = QLabel("Z Axis")
        self.step_size_spinbox_z = QDoubleSpinBox()
        self.step_size_spinbox_z.setRange(1, 100)
        self.step_size_spinbox_z.setSingleStep(1)
        self.step_size_spinbox_z.setValue(1.0)
        self.step_size_spinbox_z.valueChanged.connect(self.update_step_size_z)
        # Create a label to display the value
        self.button_increment = QPushButton('Increase')
        self.button_increment.clicked.connect(self.increment_value_z)
        self.button_decrement = QPushButton('Decrease')
        self.button_decrement.clicked.connect(self.decrement_value_z)
        # Initialize the value
        self.value = 0
        # Create a new horizontal layout for the buttons
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.step_size_spinbox_z)  # Add the spinbox to the layout
        self.buttons_layout.addWidget(self.button_increment)  # Add the increase button to the layout
        self.buttons_layout.addWidget(self.button_decrement)  # Add the decrease button to the layout
        # Add the buttons layout, label, and label to the sampleorientation_x_layout
        self.sampleorientation_z_layout.addWidget(self.sampleorientation_z_label)  # Add the label to the layout
        self.sampleorientation_z_layout.addLayout(self.buttons_layout)

        # Add the layout to the sample orientation layout
        self.sampleorientation_layout.addLayout(self.sampleorientation_x_layout)
        self.sampleorientation_layout.addLayout(self.sampleorientation_y_layout)
        self.sampleorientation_layout.addLayout(self.sampleorientation_z_layout)
        self.sampleorientation.setLayout(self.sampleorientation_layout)


        # =======================
        # Then add the each layout to the left layout
        # =======================
        
        self.left_groupbox.setLayout(self.left_groupbox_layout)
        self.left_groupbox_layout.addWidget(self.tipgeometry)
        self.left_groupbox_layout.addWidget(self.tipposition)
        self.left_groupbox_layout.addWidget(self.sampleappearance)
        self.left_groupbox_layout.addWidget(self.sampleorientation)
        
        #=======================
        #add left layout to main layout
        #=======================

        self.main_layout.addWidget(self.left_groupbox)


        """
        for right panel
        """


        # =======================
        # simulation result display
        # =======================
        self.simulationresult_layout = QVBoxLayout()
        self.simulationresult = QGroupBox("Simulation Result")
        self.simulationresult.setFixedSize(500, 400)
        self.simulationresult.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
        #check if there is dilation wave
        self.image_label = QLabel(self.simulationresult)
        config.imgdilationfig=plt.figure(num="Simlated img")
        config.imgax=config.imgdilationfig.add_subplot(111)
        plt.close(config.imgdilationfig)
        self.simulationresult_layout.addWidget(self.image_label)
        self.simulationresult.setLayout(self.simulationresult_layout)

        # =======================
        #make horizontal windget 1
        # =======================
        self.horizontal_1_layout = QHBoxLayout()


        # =======================
        #import PDB file
        # =======================
        self.importpdb_layout = QVBoxLayout()
        self.importpdb = QGroupBox("Import PDB file")
        self.importpdb.setFixedSize(450/2, 100)
        self.importpdb.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
        self.importpdb_button = QPushButton("Import")
        self.importpdb_button.clicked.connect(self.choose_pdb)
        self.file_label = QLabel()
        self.importpdb_layout.addWidget(self.importpdb_button)
        self.importpdb_layout.addWidget(self.file_label)
        

        self.importpdb.setLayout(self.importpdb_layout)
        self.horizontal_1_layout.addWidget(self.importpdb)


        # =======================
        # simulate button
        # =======================
        self.simulatebutton_layout = QVBoxLayout()
        self.simulatebutton = QPushButton("Do Simulate")
        self.simulatebutton.setFixedSize(450/2, 100)
        self.simulatebutton.setStyleSheet("QPushButton { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
        self.simulatebutton.clicked.connect(self.dosimulate)
        self.simulatebutton_layout.addWidget(self.simulatebutton)

        #self.simulatebutton.setLayout(self.simulatebutton_layout)
        self.horizontal_1_layout.addLayout(self.simulatebutton_layout)


        # =======================
        # make horizontal windget 2
        # =======================
        self.horizontal_2_layout = QHBoxLayout()

        # =======================
        # save as asd button
        # =======================
        self.saveasd_layout = QVBoxLayout()
        self.saveasd = QPushButton("Save as ASD")
        self.saveasd.setFixedSize(450/2, 50)
        self.saveasd.setStyleSheet("QPushButton { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
        self.saveasd.clicked.connect(self.saveasdfunc)
        self.saveasd_layout.addWidget(self.saveasd)
        self.horizontal_2_layout.addLayout(self.saveasd_layout)

        # =======================
        # save as png button
        # =======================
        self.savepng_layout = QVBoxLayout()
        self.savepng = QPushButton("Save as PNG")
        self.savepng.setFixedSize(450/2, 50)
        self.savepng.setStyleSheet("QPushButton { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
        self.savepng.clicked.connect(self.savepngfunc)
        self.savepng_layout.addWidget(self.savepng)
        self.horizontal_2_layout.addLayout(self.savepng_layout)


        # =======================
        # make horizontal windget 3
        # =======================
        self.horizontal_3_layout = QHBoxLayout()

        # =======================
        # save orientation button
        # =======================
        self.saveorientation_layout = QVBoxLayout()
        self.saveorientation = QPushButton("Save Orientation")
        self.saveorientation.setFixedSize(450/2, 50)
        self.saveorientation.setStyleSheet("QPushButton { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
        self.saveorientation.clicked.connect(self.saveorientationfunc)
        self.saveorientation_layout.addWidget(self.saveorientation)
        self.horizontal_3_layout.addLayout(self.saveorientation_layout)

        

        # =======================
        #Load orientation button
        # =======================
        self.loadorientation_layout = QVBoxLayout()
        self.loadorientation = QPushButton("Load Orientation")
        self.loadorientation.setFixedSize(450/2, 50)
        self.loadorientation.setStyleSheet("QPushButton { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
        self.loadorientation.clicked.connect(self.loadorientationfunc)
        self.loadorientation_layout.addWidget(self.loadorientation)
        self.horizontal_3_layout.addLayout(self.loadorientation_layout)


        # =======================
        # make horizontal windget 4
        # =======================
        self.horizontal_4_layout = QHBoxLayout()

        # =======================
        # Top view button
        # =======================
        self.topview_layout = QVBoxLayout()
        self.topview = QPushButton("Top View")
        self.topview.setFixedSize(450/3, 50)
        self.topview.setStyleSheet("QPushButton { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
        self.topview.clicked.connect(self.settopview)
        self.topview_layout.addWidget(self.topview)
        self.horizontal_4_layout.addLayout(self.topview_layout)


        # =======================
        #xz view button
        # =======================
        self.xzview_layout = QVBoxLayout()
        self.xzview = QPushButton("XZ View")
        self.xzview.setFixedSize(450/3, 50)
        self.xzview.setStyleSheet("QPushButton { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
        self.xzview.clicked.connect(self.setxzview)
        self.xzview_layout.addWidget(self.xzview)
        self.horizontal_4_layout.addLayout(self.xzview_layout)

    
        # =======================
        #yz view button
        # =======================
        self.yzview_layout = QVBoxLayout()
        self.yzview = QPushButton("YZ View")
        self.yzview.setFixedSize(450/3, 50)
        self.yzview.setStyleSheet("QPushButton { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
        self.yzview.clicked.connect(self.setyzview)
        self.yzview_layout.addWidget(self.yzview)
        self.horizontal_4_layout.addLayout(self.yzview_layout)


        # =======================
        # Then add the each layout to the right layout
        # =======================
        self.right_groupbox.setLayout(self.right_groupbox_layout)
        self.right_groupbox_layout.addWidget(self.simulationresult)
        self.right_groupbox_layout.addLayout(self.horizontal_1_layout)
        self.right_groupbox_layout.addLayout(self.horizontal_2_layout)
        self.right_groupbox_layout.addLayout(self.horizontal_3_layout)
        self.right_groupbox_layout.addLayout(self.horizontal_4_layout)


        # =======================
        # Then add the right layout to the main layout
        # =======================
        self.main_layout.addWidget(self.right_groupbox)


        # =======================
        # And finally, set the main layout to the window
        # =======================
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)



        

    """
    Funtion part
    
    """

    #=========================
    # necessary functions for tip position
    #=========================
    def update_tipposition_x_label(self, value):
        self.tipposition_x_value_label.setText(str(value))
    
    def update_tipposition_y_label(self, value):
        self.tipposition_y_value_label.setText(str(value))
    
    def update_tipposition_z_label(self, value):
        self.tipposition_z_value_label.setText(str(value))

    #=========================
    #detect step size chnaged
    #=========================
    def update_step_size_x(self):
        config.stepsize_x = self.step_size_spinbox_x.value()
        print (config.stepsize_x)
    
    def update_step_size_y(self):
        config.stepsize_y= self.step_size_spinbox_y.value()
        print (config.stepsize_y)
    
    def update_step_size_z(self):
        config.stepsize_z = self.step_size_spinbox_z.value()
        print (config.stepsize_z)


    #=========================
    # functions for change orientation
    #=========================
    def increment_value_x(self):
        config.anglex += config.stepsize_x
        #print (config.anglex)
        config.rotmatrixx= np.array([[1, 0, 0], [0, np.cos(math.radians(config.stepsize_x)), -np.sin(math.radians(config.stepsize_x))], [0, np.sin(math.radians(config.stepsize_x)), np.cos(math.radians(config.stepsize_x))]])
        config.memrotmatrix=np.dot(config.memrotmatrix, config.rotmatrixx)
        #print (config.memrotmatrix)
        print ("before roattion")
        print (len(config.pdbplot))
        coordinates = config.pdbplot[["X", "Y", "Z"]].values
        rotated_coordinates = np.dot(coordinates, config.rotmatrixx.T)
        config.pdbplot[["X", "Y", "Z"]] = rotated_coordinates
        print ("after roattion")
        print (len(config.pdbplot))
        self.display_update()


    def decrement_value_x(self):
        config.anglex -= config.stepsize_x
        print (config.anglex)
        config.rotmatrixx= np.array([[1, 0, 0], [0, np.cos(-math.radians(config.stepsize_x)), -np.sin(-math.radians(config.stepsize_x))], [0, np.sin(-math.radians(config.stepsize_x)), np.cos(-math.radians(config.stepsize_x))]])
        config.memrotmatrix=np.dot(config.memrotmatrix, config.rotmatrixx)
        print ("before roattion")
        print (len(config.pdbplot))
        coordinates = config.pdbplot[["X", "Y", "Z"]].values
        rotated_coordinates = np.dot(coordinates, config.rotmatrixx.T)
        config.pdbplot[["X", "Y", "Z"]] = rotated_coordinates
        print ("after roattion")
        print (len(config.pdbplot))
        self.display_update()


    def increment_value_y(self):
        config.angley += config.stepsize_y
        print (config.angley)
        config.rotmatrixy= np.array([[np.cos(math.radians(config.stepsize_y)), 0, np.sin(math.radians(config.stepsize_y))], [0, 1, 0], [-np.sin(math.radians(config.stepsize_y)), 0, np.cos(math.radians(config.stepsize_y))]])
        config.memrotmatrix=np.dot(config.memrotmatrix, config.rotmatrixy)
        print ("before roattion")
        print (len(config.pdbplot))
        coordinates = config.pdbplot[["X", "Y", "Z"]].values
        rotated_coordinates = np.dot(coordinates, config.rotmatrixy.T)
        config.pdbplot[["X", "Y", "Z"]] = rotated_coordinates
        print ("after roattion")
        print (len(config.pdbplot))
        self.display_update()
    
    def decrement_value_y(self):
        config.angley -= config.stepsize_y
        print (config.angley)
        config.rotmatrixy= np.array([[np.cos(-math.radians(config.stepsize_y)), 0, np.sin(-math.radians(config.stepsize_y))], [0, 1, 0], [-np.sin(-math.radians(config.stepsize_y)), 0, np.cos(-math.radians(config.stepsize_y))]])
        config.memrotmatrix=np.dot(config.memrotmatrix, config.rotmatrixy)
        print ("before roattion")
        print (len(config.pdbplot))
        coordinates = config.pdbplot[["X", "Y", "Z"]].values
        rotated_coordinates = np.dot(coordinates, config.rotmatrixy.T)
        config.pdbplot[["X", "Y", "Z"]] = rotated_coordinates
        print ("after roattion")
        print (len(config.pdbplot))
        self.display_update()
    
    def increment_value_z(self):
        config.anglez += config.stepsize_z
        print (config.anglez)
        config.rotmatrixz= np.array([[np.cos(math.radians(config.stepsize_z)), -np.sin(math.radians(config.stepsize_z)), 0], [np.sin(math.radians(config.stepsize_z)), np.cos(math.radians(config.stepsize_z)), 0], [0, 0, 1]])
        config.memrotmatrix=np.dot(config.memrotmatrix, config.rotmatrixz)
        print ("before roattion")
        print (len(config.pdbplot))
        coordinates = config.pdbplot[["X", "Y", "Z"]].values
        rotated_coordinates = np.dot(coordinates, config.rotmatrixz.T)
        config.pdbplot[["X", "Y", "Z"]] = rotated_coordinates
        print ("after roattion")
        print (len(config.pdbplot))
        self.display_update()

    def decrement_value_z(self):
        config.anglez -= config.stepsize_z
        print (config.anglez)
        config.rotmatrixz= np.array([[np.cos(-math.radians(config.stepsize_z)), -np.sin(-math.radians(config.stepsize_z)), 0], [np.sin(-math.radians(config.stepsize_z)), np.cos(-math.radians(config.stepsize_z)), 0], [0, 0, 1]])
        config.memrotmatrix=np.dot(config.memrotmatrix, config.rotmatrixz)
        print ("before roattion")
        print (len(config.pdbplot))
        coordinates = config.pdbplot[["X", "Y", "Z"]].values
        rotated_coordinates = np.dot(coordinates, config.rotmatrixz.T)
        config.pdbplot[["X", "Y", "Z"]] = rotated_coordinates
        print ("after roattion")
        print (len(config.pdbplot))
        self.display_update()

    
    #=========================
    # for import pdb file and store as dataframe
    #=========================
    def choose_pdb(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, 'QFileDialog.getOpenFileName()', '', 'PDB Files (*.pdb);;All Files (*)', options=options)
        if file:
            self.file_label.setText(file)
            parser = PDBParser()
            structure = parser.get_structure('protein', file)

            # 各アトムの情報をリストに格納
            atom_info = []
            for model in structure:
                for chain in model:
                    for residue in chain:
                        for atom in residue:
                            atom_info.append([model.id, chain.id, residue.resname, residue.id[1], atom.name, atom.coord[0], atom.coord[1], atom.coord[2]])

            # データフレームに変換しconfigに格納
            config.pdbdata = pd.DataFrame(atom_info, columns=['Model', 'Chain', 'Residue Name', 'Residue Number', 'Atom Name', 'X', 'Y', 'Z'])
            print(config.pdbdata)
            self.display_pdb_3d()

    #=========================
    # display atom 
    #=========================
            
    def display_pdb_3d(self):

        #atom type judge and display pdb as 3d plot
        if config.atomtype=="ALL":
            print("all")
            config.fig=plt.figure(num="PDB Viewer")
            config.ax = config.fig.add_subplot(111, projection='3d')
            config.sc = config.ax.scatter(config.pdbdata['X'], config.pdbdata['Y'], config.pdbdata['Z'], s=10, marker='o', alpha=0.5)
            #config.sc._offsets3d = (config.pdbdata['X'], config.pdbdata['Y'], config.pdbdata['Z'])
            config.sc.set_facecolor(config.atomtype_color[config.atomtype])
            config.sc.set_edgecolor(config.atomtype_color[config.atomtype])
            config.ax.set_xlim([config.pdbplot['X'].min(), config.pdbplot['X'].max()])
            config.ax.set_ylim([config.pdbplot['Y'].min(), config.pdbplot['Y'].max()])
            config.ax.set_zlim([config.pdbplot['Z'].min(), config.pdbplot['Z'].max()])
            config.ax.set_xlabel('X')
            config.ax.set_ylabel('Y')
            config.ax.set_zlabel('Z')
            plt.show(block=False)
            plt.draw()
        else:
            print(config.atomtype)
            #print (type(config.atomtype))
            config.pdbplot = config.pdbdata[config.pdbdata['Atom Name'] == config.atomtype]
            #print(config.pdbplot)
            print (len(config.pdbplot))
            config.fig=plt.figure(num="PDB Viewer")
            config.ax = config.fig.add_subplot(111, projection='3d')
            config.sc = config.ax.scatter(config.pdbplot['X'], config.pdbplot['Y'], config.pdbplot['Z'], s=10, marker='o', alpha=0.5)
            #config.sc._offsets3d = (config.pdbplot['X'], config.pdbplot['Y'], config.pdbplot['Z'])
            config.sc.set_facecolor(config.atomtype_color[config.atomtype])
            config.sc.set_edgecolor(config.atomtype_color[config.atomtype])
            config.ax.set_xlim([config.pdbplot['X'].min(), config.pdbplot['X'].max()])
            config.ax.set_ylim([config.pdbplot['Y'].min(), config.pdbplot['Y'].max()])
            config.ax.set_zlim([config.pdbplot['Z'].min(), config.pdbplot['Z'].max()])
            config.ax.set_xlabel('X')
            config.ax.set_ylabel('Y')
            config.ax.set_zlabel('Z')
            plt.show(block=False)
            plt.draw()

    
    #=========================
    # atomtype chnaged display update
    #=========================
    def display_atomtype_update(self):
        print ("update")
        if config.atomtype=="ALL":
            print("all")
            config.pdbplot = config.pdbdata
            print (len(config.pdbplot))
            config.sc._offsets3d = (config.pdbdata['X'], config.pdbdata['Y'], config.pdbdata['Z'])
            config.sc.set_facecolor(config.atomtype_color[config.atomtype])
            config.sc.set_edgecolor(config.atomtype_color[config.atomtype])
            config.ax.set_xlim([config.pdbplot['X'].min(), config.pdbplot['X'].max()])
            config.ax.set_ylim([config.pdbplot['Y'].min(), config.pdbplot['Y'].max()])
            config.ax.set_zlim([config.pdbplot['Z'].min(), config.pdbplot['Z'].max()])
            config.ax.set_xlabel('X')
            config.ax.set_ylabel('Y')
            config.ax.set_zlabel('Z')
            plt.draw()
        else:
            print(config.atomtype)
            config.pdbplot = config.pdbdata[config.pdbdata['Atom Name'] == config.atomtype]
            #print(config.pdbplot)
            print (len(config.pdbplot))
            config.sc._offsets3d = (config.pdbplot['X'], config.pdbplot['Y'], config.pdbplot['Z'])
            config.sc.set_facecolor(config.atomtype_color[config.atomtype])
            config.sc.set_edgecolor(config.atomtype_color[config.atomtype])
            config.ax.set_xlim([config.pdbplot['X'].min(), config.pdbplot['X'].max()])
            config.ax.set_ylim([config.pdbplot['Y'].min(), config.pdbplot['Y'].max()])
            config.ax.set_zlim([config.pdbplot['Z'].min(), config.pdbplot['Z'].max()])
            config.ax.set_xlabel('X')
            config.ax.set_ylabel('Y')
            config.ax.set_zlabel('Z')
            plt.draw()

        
       
    
    #=========================
    #pdb display update
    #=========================
    def display_update(self):
        config.sc._offsets3d = (config.pdbplot['X'], config.pdbplot['Y'], config.pdbplot['Z'])
        config.sc.set_facecolor(config.atomtype_color[config.atomtype])
        config.sc.set_edgecolor(config.atomtype_color[config.atomtype])
        config.ax.set_xlim([config.pdbplot['X'].min(), config.pdbplot['X'].max()])
        config.ax.set_ylim([config.pdbplot['Y'].min(), config.pdbplot['Y'].max()])
        config.ax.set_zlim([config.pdbplot['Z'].min(), config.pdbplot['Z'].max()])
        config.ax.set_xlabel('X')
        config.ax.set_ylabel('Y')
        config.ax.set_zlabel('Z')
        plt.draw()




    #=========================
    # Do tip sample dilation simulation
    #=========================
    def dosimulate(self):
        print("simulate")
        #do simulation with python
        #self.dilation()
        # print(type(config.tipradius))
        # print(type(config.tipshape))
        # print(type(config.tipsize))
        # print(type(config.zcoordinate))
        # print(type(config.tipangle))
        # print(type(config.xcoordinate))
        # print(type(config.pdbplot["X"]))
        # print(type(config.pixelxdirection))
        # print(type(config.dx))
        # print(type(config.dy))
        
        #do simulation with cython
        print(type(config.tipradius))
        print(type(config.tipshape))
        print(type(config.tipangle))
        config.pdbplot_x=config.pdbplot["X"].to_numpy(dtype=np.float32)
        config.pdbplot_y=config.pdbplot["Y"].to_numpy(dtype=np.float32)
        config.pdbplot_z=config.pdbplot["Z"].to_numpy(dtype=np.float32)
        print(type(config.pdbplot_x))
        print(type(config.pdbplot_y))
        print(type(config.pdbplot_z))
        result =dilationfunctionmodule.dilation(config.pdbplot_x, config.pdbplot_y, config.pdbplot_z, config.pixelxdirection, config.tipradius, config.tipshape, config.tipangle)
        print(result)
        
        # self.dilation_display_update()
        # plt.show(block=False)
        

    #=========================
    #save as png
    #=========================
    def savepngfunc(self):
        print("save png")
        plt.imsave('simulatedafm.png',config.savepng)
        print ("saved")
    

    #=========================
    # save as asd file
    #=========================
    def saveasdfunc(self):
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix('.asd')
        
        if file_dialog.exec_() == QFileDialog.Accepted:
            save_file_path = file_dialog.selectedFiles()[0]


            if save_file_path:
                
                FileType = 1
                FileHeaderSizeForSave = 165 + len("Nobody") + len("Simulated Image")
                FrameHeaderSize = 32
                TextEncoding = 932
                OpeNameSize = 9
                CommentSizeForSave = 0  # コメントの長さに応じて修正が必要
                DataType1ch = 20564
                DataType2ch = 0
                FrameNum = 1
                ImageNum = 1
                ScanDirection = 0
                ScanTryNum = 1
                TXPixel = config.dilation.shape[1]
                TYPixel = config.dilation.shape[0]
                TXScanSize = round(TXPixel * config.dx)
                TYScanSize = round(TYPixel * config.dy)
                AveFlag = 0
                AverageNum = 1
                Year = 2023  # 年に応じて修正が必要
                Month = 5  # 月に応じて修正が必要
                Day = 16  # 日に応じて修正が必要
                Hour = 12  # 時に応じて修正が必要
                Minute = 0  # 分に応じて修正が必要
                Second = 0  # 秒に
                XRound = 0
                YRound = 0
                FrameTime = 1.0
                Sensitivity = 1.0
                PhaseSens = 1.0
                Offset = 0  # Offsetの値に応じて修正が必要
                MachineNo = 1
                ADRange = 262144
                ADResolution = 12
                MaxScanSizeX = 4000
                MaxScanSizeY = 1700
                PiezoConstX = 1.0
                PiezoConstY = 1.0
                PiezoConstZ = 20.0
                DriverGainZ = 2.0
                Maxdata=2775
                Minidata=2716

                OpeName = "Nobody"
                Comment = "Simulated Image"
                
                ImageIndex=1
                LaserFlag=0
                CurrentNum=1
                Xoffset=0
                Yoffset=0
                Xtilt=0
                Ytilt=0
                show2chflag=0
                Reserved=0

                index=0


                # ファイルの作成とデータの書き込み
                with open(save_file_path, "wb") as f:
                    # ヘッダ情報の書き込み

                    f.write(struct.pack('i', FileType))
                    f.write(struct.pack('i', FileHeaderSizeForSave))
                    f.write(struct.pack('i', FrameHeaderSize))
                    f.write(struct.pack('i', TextEncoding))
                    f.write(struct.pack('i', OpeNameSize))
                    f.write(struct.pack('i', CommentSizeForSave))
                    f.write(struct.pack('i', DataType1ch))
                    f.write(struct.pack('i', DataType2ch))
                    f.write(struct.pack('i', FrameNum))
                    f.write(struct.pack('i', ImageNum))
                    f.write(struct.pack('i', ScanDirection))
                    f.write(struct.pack('i', ScanTryNum))
                    f.write(struct.pack('i', TXPixel))
                    f.write(struct.pack('i', TYPixel))
                    f.write(struct.pack('i', TXScanSize))
                    f.write(struct.pack('i', TYScanSize))
                    f.write(struct.pack('B', AveFlag))
                    f.write(struct.pack('i', AverageNum))
                    f.write(struct.pack('i', Year))
                    f.write(struct.pack('i', Month))
                    f.write(struct.pack('i', Day))
                    f.write(struct.pack('i', Hour))
                    f.write(struct.pack('i', Minute))
                    f.write(struct.pack('i', Second))
                    f.write(struct.pack('i', XRound))
                    f.write(struct.pack('i', YRound))
                    f.write(struct.pack('f', FrameTime))
                    f.write(struct.pack('f', Sensitivity))
                    f.write(struct.pack('f', PhaseSens))
                    f.write(struct.pack('i', Offset))
                    f.write(struct.pack('i', Offset))
                    f.write(struct.pack('i', Offset))
                    f.write(struct.pack('i', Offset))
                    f.write(struct.pack('i', MachineNo))
                    f.write(struct.pack('i', ADRange))
                    f.write(struct.pack('i', ADResolution))
                    f.write(struct.pack('f', MaxScanSizeX))
                    f.write(struct.pack('f', MaxScanSizeY))
                    f.write(struct.pack('f', PiezoConstX))
                    f.write(struct.pack('f', PiezoConstY))
                    f.write(struct.pack('f', PiezoConstZ))
                    f.write(struct.pack('f', DriverGainZ))
                    
                    # オペレータ名とコメントの書き込み
                    f.write(OpeName.encode("utf-8"))
                    f.write(Comment.encode("utf-8"))
                    
                    f.seek(FileHeaderSizeForSave + (FrameHeaderSize + 2 * TXPixel * TYPixel) * index)
                    print (FileHeaderSizeForSave + (FrameHeaderSize + 2 * TXPixel * TYPixel) * index)
                    CurrentNum=0
                    Maxdata=round(np.max(config.dilation))
                    Minidata=round(np.min(config.dilation))
                    f.write(struct.pack('I', CurrentNum))
                    f.write(struct.pack('H', Maxdata))
                    f.write(struct.pack('H', Minidata))
                    f.write(struct.pack('h', Xoffset))
                    f.write(struct.pack('h', Yoffset))
                    f.write(struct.pack('f', Xtilt))
                    f.write(struct.pack('f', Ytilt))
                    f.write(struct.pack('B', LaserFlag))
                    f.write(struct.pack('B', Reserved))
                    f.write(struct.pack('h', Reserved))
                    f.write(struct.pack('i', Reserved))
                    f.write(struct.pack('i', Reserved))


                    
                    
                    for Ynum in range(TYPixel):
                        for Xnum in range(TXPixel):
                            data = ((5.0 - config.dilation[Ynum][Xnum] / PiezoConstZ / DriverGainZ) * 4096.0) / 10.0
                            f.write(struct.pack('f', data))
                f.close()


    #=========================
    # detect atom type chnage
    #=========================
    def atomtype_change(self, index):
        self.current_atom = self.sampleatom.itemText(index)
        config.atomtype = self.current_atom
        print(config.atomtype)
        self.display_atomtype_update()

    #=========================
    # detect tip radius chnage
    #=========================
    def tipradius_change(self):
        config.tipradius = self.tipradius.value()
        print(config.tipradius)
        #self.createtip() #というよりdodimulationにするべき
    
    #=========================
    #detect tip shape change
    #=========================
    def tipshape_change(self, index):
        self.current_tipshape = self.tipshape.itemText(index)
        config.tipshape = self.current_tipshape
        print(config.tipshape)
        # self.createtip()

    
    #=========================
    #detect pixel x direction change
    #=========================
    def pixelxdirection_change(self):
        config.pixelxdirection = self.pixelxdirection.value()
        print(config.pixelxdirection)
        # self.createtip()
    
    #=========================
    #detect tip angle change
    #=========================
    def tipangle_change(self):
        config.tipangle = self.tipangle.value()
        print(config.tipangle)
        # self.createtip()

    #=========================
    # if dilation wave is updated check
    #=========================
    def dilation_display_update(self):
        #print ("updated")
        #self.image_label=QLabel(self.simulationresult)
        #img=Image.fromarray(img_array)
        #img.save('dilation.png')
        
        #config.imgax.clear()
        img_array=(config.dilation/config.dilation.max())*255
        img_array=img_array.astype(np.uint8)
        #print (img_array.shape)
        #np.savetxt('dilation_255.csv', img_array, delimiter=',')
        cmap=self.makeDIcolor()
        #img_array=cv2.applyColorMap(img_array, config.DIcolor)
        #img_array=cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
        config.savepng=cmap(img_array)
        #plt.imsave('dilation.png',config.savepng)
        #config.imgfig=plt.figure(num="dilation img")
        #config.imgax=config.imgfig.add_subplot(111)
        config.imgax.imshow(img_array,extent=[0,config.dx*img_array.shape[1],0,config.dy*img_array.shape[0]],cmap=cmap)
        config.imgax.set_xlabel("x nm")
        config.imgax.set_ylabel("y nm")
        buf=io.BytesIO()
        config.imgdilationfig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        buf.seek(0) 
        config.dilation_qimage=QImage.fromData(buf.getvalue())
        config.dilation_map=QPixmap.fromImage(config.dilation_qimage)
        config.dilation_map=config.dilation_map.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)
        self.image_label.setPixmap(QPixmap(config.dilation_map))
        plt.show(block=False)
        
        
    

    
    #=========================
    # create tip
    #=========================
    def createtip(self):
        print("create tip")
        createtipstart=datetime.datetime.now()
        print ("create tip start time: "+str(createtipstart)) 
        

        z_off = (config.tipradius / 2) / math.tan(config.tipangle * math.pi / 180) ** 2
        r_crit=config.tipradius/math.tan(config.tipangle*math.pi/180)
        z_crit=r_crit/math.tan(config.tipangle*math.pi/180)-z_off

        # print(type(z_off))
        # print(type(r_crit))
        # print(type(z_crit))

        if config.tipshape=="Paraboloid":
            i_xm=(1/config.dx)*math.sqrt(2*config.tipradius*(config.zcoordinate.max()-config.zcoordinate.min()))
            # print("i_xm")
            # print(type(i_xm))
            config.tipsize=2*math.ceil(i_xm)+1
            # print("tipsize")
            # print(type(config.tipsize))

            #print ("paraboloid")
        
        elif config.tipshape=="Cone":
            r_crit=config.tipradius/math.sqrt(1+math.tan(config.tipangle*math.pi/180)**2)
            z_crit=r_crit*math.tan(config.tipangle*math.pi/180)-z_off
            z_off=-config.tipradius+math.sqrt(config.tipradius**2-r_crit**2)+r_crit**2/math.sqrt(config.tipradius**2-r_crit**2)
            if z_crit>config.zcoordinate.max():
                i_xm=(1/config.dx)*math.sqrt(config.tipradius**2-(config.tipradius-(config.zcoordinate.max()-config.zcoordinate.min()))**2)
            else:
                i_xm=(1/config.dx)*((config.zcoordinate.max()-config.zcoordinate.min())+z_off)*math.tan(config.tipangle*math.pi/180)
            config.tipsize=2*math.ceil(i_xm)+1
            # print(type(z_off))
            # print(type(r_crit))
            # print(type(z_crit))

            # print("i_xm")
            # print(type(i_xm))
            # print("tipsize")
            # print(type(config.tipsize))
        
                             
        config.tipsize_half=math.trunc(config.tipsize/2)+1

        if config.tipsize%2==0:
            config.tipsize=config.tipsize+1
        centerdistance=(config.tipsize-1)/2
        config.tipwave=np.zeros((config.tipsize,config.tipsize))

        #print (config.tipsize)

        if config.tipshape=="Paraboloid":
            for iy in range(0,config.tipsize):
                for ix in range(0,config.tipsize):
                    config.tipwave[iy][ix]=(1/(2*config.tipradius))*(((ix - centerdistance)*config.dx)**2 + ((iy - centerdistance)*config.dy)**2)
        elif config.tipshape=="Cone":
            curvewave=np.zeros((config.tipsize,config.tipsize))
            conewave=np.zeros((config.tipsize,config.tipsize))
            r_crit=config.tipradius/math.sqrt(1+math.tan(config.tipangle*math.pi/180)**2)
            z_off=-config.tipradius+math.sqrt(config.tipradius**2-r_crit**2)+r_crit**2/math.sqrt(config.tipradius**2-r_crit**2)
            for iy in range(0,config.tipsize):
                for ix in range(0,config.tipsize):
                    xpos=(ix - centerdistance)*config.dx
                    ypos=(iy - centerdistance)*config.dy
                    r_i=math.sqrt(xpos**2+ypos**2)
                    if r_i<=r_crit:
                        config.tipwave[iy][ix]=config.tipradius-math.sqrt(config.tipradius**2-r_i**2)
                    else:
                        config.tipwave[iy][ix]=r_i/math.tan(config.tipangle*math.pi/180)-z_off
                    

        createtipend=datetime.datetime.now()
        print ("create tip start time: "+str(createtipend)) 
        print ("create tip time: "+str(createtipend-createtipstart))
        
        

        
       
    #=========================
    # one pixel dilation
    #=========================
    def onepixeldilation(self):
        print ("one pixel dilation")
        onepixelstart=datetime.datetime.now()
        print ("one pixel dilation start time: "+str(onepixelstart))
        #config.onepixeldilation=np.zeros((config.pixelxdirection+2*config.tipsize, config.pixelydirection+2*config.tipsize))
        
        #make height map
        config.onepixeldilation=np.zeros((config.grid_sizex,config.grid_sizey))

        for iy in range(0,config.grid_sizey):
            for ix in range(0,config.grid_sizex):
                z_max=0
                bol_vec=(  (config.ycoordinate>=(iy-1)*config.dy) & (config.ycoordinate<(iy)*config.dy)& (config.xcoordinate>=(ix-1)*config.dx) & (config.xcoordinate<(ix)*config.dx)  &  (config.zcoordinate>(z_max)))
                red_coord = bol_vec*config.zcoordinate
                z_max=red_coord.max()
                config.onepixeldilation[ix][iy]=z_max

        onepixelend=datetime.datetime.now()
        print ("one pixel dilation end time: "+str(onepixelend))
        print ("one pixel dilation time: "+str(onepixelend-onepixelstart))
        
    
    # #=========================
    # one pixel dilation multi thread
    # #=========================

    # def onepixeldilation(self):
    #     print("one pixel dilation")
    #     onepixelstart = datetime.datetime.now()
    #     print("one pixel dilation start time: " + str(onepixelstart))
        
    #     config.onepixeldilation = np.zeros((config.grid_sizex, config.grid_sizey), dtype=np.float32)

    #     with ThreadPoolExecutor() as executor:
    #         futures = []
    #         for iy in range(config.grid_sizey):
    #             for ix in range(config.grid_sizex):
    #                 future = executor.submit(self.calculate_pixel_value, iy, ix)
    #                 futures.append(future)
            
    #         for future in futures:
    #             future.result()
    #     print(config.onepixeldilation)
    #     onepixelend = datetime.datetime.now()
    #     print("one pixel dilation end time: " + str(onepixelend))
    #     print("one pixel dilation time: " + str(onepixelend - onepixelstart))

    # def calculate_pixel_value(self, iy, ix):
    #     y_min = (iy - 1) * config.dy
    #     y_max = iy * config.dy
    #     x_min = (ix - 1) * config.dx
    #     x_max = ix * config.dx
        
    #     mask = (
    #         (config.ycoordinate >= y_min) &
    #         (config.ycoordinate < y_max) &
    #         (config.xcoordinate >= x_min) &
    #         (config.xcoordinate < x_max) &
    #         (config.zcoordinate > 0)
    #     )
    #     z_max = np.max(config.zcoordinate[mask])
    #     config.onepixeldilation[ix, iy] = z_max
    
  
    #=========================
    # make dilation
    #=========================
    def dilation(self):
        starttime = datetime.datetime.now()
        print ("Start time: " + str(starttime))
        config.xcoordinate=config.pdbplot['X']-config.pdbplot['X'].min()
        config.ycoordinate=config.pdbplot['Y']-config.pdbplot['Y'].min()
        config.zcoordinate=config.pdbplot['Z']-config.pdbplot['Z'].min()

        config.xcoordinate=config.xcoordinate/10
        config.ycoordinate=config.ycoordinate/10
        config.zcoordinate=config.zcoordinate/10

        #get the number of the atoms
        atomnumber=len(config.pdbplot)
        #set the number of pixels
        config.grid_sizex=config.pixelxdirection
        config.grid_sizey=math.ceil(config.pixelxdirection*(config.ycoordinate.max()/config.xcoordinate.max()))

        #set resolution nm/pixel
        config.dx=(config.xcoordinate.max())/config.grid_sizex
        config.dy=(config.ycoordinate.max())/config.grid_sizey
        
        self.onepixeldilation()
        #make tip
        self.createtip()
        #print("after create tip")
        #print (config.tipsize)
        #print (config.tipwave.shape)

        l_x=config.grid_sizex+2*config.tipsize
        l_y=config.grid_sizey+2*config.tipsize
        config.dilationborder=np.zeros((l_x,l_y))
        config.dilationborder[config.tipsize:l_x-config.tipsize,config.tipsize:l_y-config.tipsize]=config.onepixeldilation
        img_array_border=(config.dilationborder/config.dilationborder.max())*255
        img_array_border=img_array_border.astype(np.uint8)
        
        config.dilation=np.zeros((l_x,l_y))
        #print (l_x)
        #print (l_y)


        #make dilation
        for ix in range(0,l_x-config.tipwave.shape[0]):
            for iy in range(0,l_y-config.tipwave.shape[1]):
                
                z_diffmap=config.dilationborder[ix:ix+config.tipsize,iy:iy+config.tipsize]-config.tipwave
                displacement=z_diffmap.max()
                config.dilation[ix+config.tipsize_half][iy+config.tipsize_half]=displacement
        
       
        np.savetxt('dilation.csv', config.dilation, delimiter=',')
        

        endtime = datetime.datetime.now()
        print ("End time: " + str(endtime))
        print ("Simulation time: " + str(endtime - starttime))
        self.dilation_display_update()
        plt.show(block=False)
       



    #=========================
    # make color map
    #=========================
    def makeDIcolor(self):

        rgb_values = np.loadtxt("rgb.csv",delimiter=',') 
        cmap = LinearSegmentedColormap.from_list("my_cmap", rgb_values)
        cmap=cmap.reversed()
        return cmap
    
    #=========================
    # save orientation
    #=========================
    def saveorientationfunc(self):
        config.memrotmatrix
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix('.txt')
        file_dialog.exec_()
        file_path = file_dialog.selectedFiles()[0]

        if file_path:
            # 保存するデータを準備 (例: ダミーデータ)
            data = config.memrotmatrix

            # ファイルに保存
            np.savetxt(file_path, data)
    
    #=========================
    # load orientation
    #=========================
    def loadorientationfunc(self):
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        file_dialog.setDefaultSuffix('.txt')
        file_dialog.exec_()
        file_path = file_dialog.selectedFiles()[0]

        if file_path:
            # ファイルから読み込み
            data = np.loadtxt(file_path)
            config.memrotmatrix=data
            self.orientationdisplay_update()
            
    #=========================
    # update orientation by loading memrotmatrix
    #=========================
    def orientationdisplay_update(self):
        coordinates = config.pdbplot[["X", "Y", "Z"]].values
        rotated_coordinates = np.dot(coordinates, config.memrotmatrix.T)
        config.pdbplot[["X", "Y", "Z"]] = rotated_coordinates
        print ("after rload orientation")
        print (len(config.pdbplot))
        self.display_update()
    
    #=========================
    # set top view xy view
    #=========================
    def settopview(self):
        config.sc._offsets3d = (config.pdbplot['X'], config.pdbplot['Y'], config.pdbplot['Z'])
        config.sc.set_facecolor(config.atomtype_color[config.atomtype])
        config.sc.set_edgecolor(config.atomtype_color[config.atomtype])
        config.ax.set_xlim([config.pdbplot['X'].min(), config.pdbplot['X'].max()])
        config.ax.set_ylim([config.pdbplot['Y'].min(), config.pdbplot['Y'].max()])
        config.ax.set_zlim([config.pdbplot['Z'].min(), config.pdbplot['Z'].max()])
        config.ax.set_xlabel('X')
        config.ax.set_ylabel('Y')
        config.ax.set_zlabel('Z')
        config.ax.view_init(elev=90, azim=0)  # XY平面から見た角度に設定
        plt.draw()
    
    #=========================
    # set side view xz view
    #=========================
    def setxzview(self):
        config.sc._offsets3d = (config.pdbplot['X'], config.pdbplot['Y'], config.pdbplot['Z'])
        config.sc.set_facecolor(config.atomtype_color[config.atomtype])
        config.sc.set_edgecolor(config.atomtype_color[config.atomtype])
        config.ax.set_xlim([config.pdbplot['X'].min(), config.pdbplot['X'].max()])
        config.ax.set_ylim([config.pdbplot['Y'].min(), config.pdbplot['Y'].max()])
        config.ax.set_zlim([config.pdbplot['Z'].min(), config.pdbplot['Z'].max()])
        config.ax.set_xlabel('X')
        config.ax.set_ylabel('Y')
        config.ax.set_zlabel('Z')
        config.ax.view_init(elev=0, azim=0)
        plt.draw()
    
    #=========================
    # set side view yz view
    #=========================
    def setyzview(self):
        config.sc._offsets3d = (config.pdbplot['X'], config.pdbplot['Y'], config.pdbplot['Z'])
        config.sc.set_facecolor(config.atomtype_color[config.atomtype])
        config.sc.set_edgecolor(config.atomtype_color[config.atomtype])
        config.ax.set_xlim([config.pdbplot['X'].min(), config.pdbplot['X'].max()])
        config.ax.set_ylim([config.pdbplot['Y'].min(), config.pdbplot['Y'].max()])
        config.ax.set_zlim([config.pdbplot['Z'].min(), config.pdbplot['Z'].max()])
        config.ax.set_xlabel('X')
        config.ax.set_ylabel('Y')
        config.ax.set_zlabel('Z')
        config.ax.view_init(elev=0, azim=90)
        plt.draw()
    





                        






                        

                        
                    

                    
                


