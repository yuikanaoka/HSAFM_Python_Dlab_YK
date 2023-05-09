# -------------------------------------------------------------------------------
# Name:        simulation.py
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
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt


import numpy as np
import time
import threading
import datetime

import cv2

from filelist import FileList
from imagefifo import FileImport

import config
import lineprofile as lp
import removebackground as rb
import noisefilter as nf

class TipSampleDilationWindow(QtWidgets.QWidget):

    def __init__(self,parent=None):

        super(TipSampleDilationWindow, self).__init__(parent)
        
    
        
        result = config.get_savedparam("panel", "Tip Sample Dilation")
        if result is not None:
          # 一致する行が見つかった場合は、resultを処理する
            config.panel_left, config.panel_top, config.panel_width, config.panel_height = result
        else:
            config.panel_width= 500
            config.panel_height = 700
            config.panel_top = 100
            config.panel_left = 100

        self.setGeometry(config.panel_left , config.panel_top , config.panel_width, config.panel_height) 

        self.setWindowTitle("Tip Sample Dilation")

        self.main_layout = QVBoxLayout()

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

        #tip shape
        self.tipshape_layout = QVBoxLayout()  # Create a new QVBoxLayout for the shape
        self.tipshape_label = QLabel("Tip Shape")
        self.tipshape = QComboBox()
        self.tipshape.addItem("Cone")
        self.tipshape.addItem("Palaroid")
        self.tipshape_layout.addWidget(self.tipshape_label)
        self.tipshape_layout.addWidget(self.tipshape)

        #pixel x direction
        self.pixelxdirection_layout = QVBoxLayout()  # Create a new QVBoxLayout for the shape
        self.pixelxdirection_label = QLabel("Pixel x direction")
        self.pixelxdirection = QDoubleSpinBox()
        self.pixelxdirection.setRange(50, 100)
        self.pixelxdirection_layout.addWidget(self.pixelxdirection_label)
        self.pixelxdirection_layout.addWidget(self.pixelxdirection)

        #tip angle
        self.tipangle_layout = QVBoxLayout()  # Create a new QVBoxLayout for the shape
        self.tipangle_label = QLabel("Tip Angle")
        self.tipangle = QDoubleSpinBox()
        self.tipangle.setRange(1, 10)
        self.tipangle_layout.addWidget(self.tipangle_label)
        self.tipangle_layout.addWidget(self.tipangle)



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
        self.tipposition.setFixedSize(450, 300)
        self.tipposition.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px

        #tip position x
        self.tipposition_x_layout = QVBoxLayout()  # Create a new QVBoxLayout for the tip postion
        self.tipposition_x_label = QLabel("X position") 
        self.tipposition_x = QSlider(Qt.Horizontal)
        self.tipposition_x.setRange(-100, 100)
        self.tipposition_x.setSingleStep(5)
        self.tipposition_x.setValue(0)
        self.tipposition_x_value_label = QLabel()  # Create a new QLabel to display the value
        # Update the text of the value label when the value of the slider changes
        def update_value_label(value):
            self.tipposition_x_value_label.setText(str(value))
            # Connect the valueChanged signal of the slider to the update_value_label function
        self.tipposition_x.valueChanged.connect(update_value_label)
        # Initialize the value label
        update_value_label(self.tipposition_x.value())

        # Add the widgets to the layout
        self.tipposition_x_layout.addWidget(self.tipposition_x_label)
        self.tipposition_x_layout.addWidget(self.tipposition_x)
        self.tipposition_x_layout.addWidget(self.tipposition_x_value_label)  # Add the value label to the layout

        #tip position y
        self.tipposition_y_layout = QVBoxLayout()  # Create a new QVBoxLayout for the tip postion
        self.tipposition_y_label = QLabel("Y position")
        self.tipposition_y = QSlider(Qt.Horizontal)
        self.tipposition_y.setRange(-100, 100)
        self.tipposition_y.setSingleStep(5)
        self.tipposition_y.setValue(0)
        self.tipposition_y_value_label = QLabel()  # Create a new QLabel to display the value
        # Update the text of the value label when the value of the slider changes
        def update_value_label(value):
            self.tipposition_y_value_label.setText(str(value))
            # Connect the valueChanged signal of the slider to the update_value_label function
        self.tipposition_y.valueChanged.connect(update_value_label)
        # Initialize the value label
        update_value_label(self.tipposition_y.value())

        # Add the widgets to the layout
        self.tipposition_y_layout.addWidget(self.tipposition_y_label)
        self.tipposition_y_layout.addWidget(self.tipposition_y)
        self.tipposition_y_layout.addWidget(self.tipposition_y_value_label)  # Add the value label to the layout

        # tip position z
        self.tipposition_z_layout = QVBoxLayout()  # Create a new QVBoxLayout for the tip postion
        self.tipposition_z_label = QLabel("Z position")
        self.tipposition_z = QSlider(Qt.Horizontal)
        self.tipposition_z.setRange(-100, 100)
        self.tipposition_z.setSingleStep(5)
        self.tipposition_z.setValue(0)
        self.tipposition_z_value_label = QLabel()  # Create a new QLabel to display the value
        # Update the text of the value label when the value of the slider changes
        def update_value_label(value):
            self.tipposition_z_value_label.setText(str(value))
            # Connect the valueChanged signal of the slider to the update_value_label function
        self.tipposition_z.valueChanged.connect(update_value_label)
        # Initialize the value label
        update_value_label(self.tipposition_z.value())

        # Add the widgets to the layout
        self.tipposition_z_layout.addWidget(self.tipposition_z_label)
        self.tipposition_z_layout.addWidget(self.tipposition_z)
        self.tipposition_z_layout.addWidget(self.tipposition_z_value_label)  # Add the value label to the layout


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
        self.sampleorientation_layout = QHBoxLayout()
        self.sampleorientation = QGroupBox("Sample Orientation")
        self.sampleorientation.setFixedSize(450, 200)
        self.sampleorientation.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
        
        #sample orientation x
        self.sampleorientation_x_layout = QVBoxLayout()  # Create a new QVBoxLayout for the tip postion
        self.sampleorientation_x_label = QLabel("X Axis")
        # Create a label to display the value
        self.value=1
        self.value_label = QLabel(str(self.value))
        self.button = QPushButton('Click me')
        self.button.clicked.connect(self.increment_value)

        

        # Add the button and label to the layout
        self.sampleorientation_x_layout.addWidget(self.sampleorientation_x_label)  # Add the label to the layout
        self.sampleorientation_x_layout.addWidget(self.button)  # Add the button to the layout
        self.sampleorientation_x_layout.addWidget(self.value_label)  # Add the value label to the layout


        # add the layout to the sample orientation layout
        self.sampleorientation_layout.addLayout(self.sampleorientation_x_layout)
        self.sampleorientation.setLayout(self.sampleorientation_layout)






        # =======================
        # Then add the each layout to the main layout
        # =======================
        self.main_layout.addWidget(self.tipgeometry)
        self.main_layout.addWidget(self.tipposition)
        self.main_layout.addWidget(self.sampleappearance)
        self.main_layout.addWidget(self.sampleorientation)


        # =======================
        # And finally, set the main layout to the window
        # =======================
        self.setLayout(self.main_layout)


    #=========================
    # necessary functions for change orientation
    #=========================

    def increment_value(self):
                self.value += 1
                self.value_label.setText(str(self.value))

    def decrement_value(self):
        self.value -= 1
        self.value_label.setText(str(self.value))