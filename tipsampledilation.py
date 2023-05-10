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

from Bio.PDB import PDBParser
import pandas as pd


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
            config.panel_height = 800
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
        self.step_size_spinbox = QDoubleSpinBox()
        self.step_size_spinbox.setRange(1, 100)
        self.step_size_spinbox.setSingleStep(1)
        self.step_size_spinbox.setValue(1.0)
        # Create a label to display the value
        self.button_increment = QPushButton('Increase')
        self.button_increment.clicked.connect(self.increment_value)
        self.button_decrement = QPushButton('Decrease')
        self.button_decrement.clicked.connect(self.decrement_value)
        # Initialize the value
        self.value = 0
        # Create a new horizontal layout for the buttons
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.step_size_spinbox)  # Add the spinbox to the layout
        self.buttons_layout.addWidget(self.button_increment)  # Add the increase button to the layout
        self.buttons_layout.addWidget(self.button_decrement)  # Add the decrease button to the layout
        # Add the buttons layout, label, and label to the sampleorientation_x_layout
        self.sampleorientation_x_layout.addWidget(self.sampleorientation_x_label)  # Add the label to the layout
        self.sampleorientation_x_layout.addLayout(self.buttons_layout)


        #sample orientation y
        self.sampleorientation_y_layout = QVBoxLayout()  # Create a new QVBoxLayout for the tip postion
        self.sampleorientation_y_label = QLabel("Y Axis")
        self.step_size_spinbox = QDoubleSpinBox()
        self.step_size_spinbox.setRange(1, 100)
        self.step_size_spinbox.setSingleStep(1)
        self.step_size_spinbox.setValue(1.0)
        # Create a label to display the value
        self.button_increment = QPushButton('Increase')
        self.button_increment.clicked.connect(self.increment_value)
        self.button_decrement = QPushButton('Decrease')
        self.button_decrement.clicked.connect(self.decrement_value)
        # Initialize the value
        self.value = 0
        #self.step_size = self.step_size_spinbox.value()
        # Create a new horizontal layout for the buttons
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.step_size_spinbox)  # Add the spinbox to the layout
        self.buttons_layout.addWidget(self.button_increment)  # Add the increase button to the layout
        self.buttons_layout.addWidget(self.button_decrement)  # Add the decrease button to the layout
        # Add the buttons layout, label, and label to the sampleorientation_x_layout
        self.sampleorientation_y_layout.addWidget(self.sampleorientation_y_label)  # Add the label to the layout
        self.sampleorientation_y_layout.addLayout(self.buttons_layout)


        #sample orientation z
        self.sampleorientation_z_layout = QVBoxLayout()  # Create a new QVBoxLayout for the tip postion
        self.sampleorientation_z_label = QLabel("Z Axis")
        self.step_size_spinbox = QDoubleSpinBox()
        self.step_size_spinbox.setRange(1, 100)
        self.step_size_spinbox.setSingleStep(1)
        self.step_size_spinbox.setValue(1.0)
        # Create a label to display the value
        self.button_increment = QPushButton('Increase')
        self.button_increment.clicked.connect(self.increment_value)
        self.button_decrement = QPushButton('Decrease')
        self.button_decrement.clicked.connect(self.decrement_value)
        # Initialize the value
        self.value = 0
        # Create a new horizontal layout for the buttons
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.step_size_spinbox)  # Add the spinbox to the layout
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
    # necessary functions for tip position
    #=========================
    def update_tipposition_x_label(self, value):
        self.tipposition_x_value_label.setText(str(value))
    
    def update_tipposition_y_label(self, value):
        self.tipposition_y_value_label.setText(str(value))
    
    def update_tipposition_z_label(self, value):
        self.tipposition_z_value_label.setText(str(value))

    #=========================
    # necessary functions for change orientation
    #=========================
    def increment_value(self):
        self.value += self.step_size_spinbox.value()
        print (self.value)

    def decrement_value(self):
        self.value -= self.step_size_spinbox.value()
        print (self.value)


    

# =======================
# simulaion window
# =======================


class SimulationWindow(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(SimulationWindow, self).__init__(parent)
        result = config.get_savedparam("panel", "Simulation Window")
        if result is not None:
          # 一致する行が見つかった場合は、resultを処理する
            config.panel_left, config.panel_top, config.panel_width, config.panel_height = result
        else:
            config.panel_width= 500
            config.panel_height = 800
            config.panel_top = 100
            config.panel_left = 100

        self.setGeometry(config.panel_left , config.panel_top , config.panel_width, config.panel_height) 

        self.setWindowTitle("Simulation Window")

        self.main_layout = QVBoxLayout()

        # =======================
        # simulation result display
        # =======================
        self.simulationresult_layout = QVBoxLayout()
        self.simulationresult = QGroupBox("Simulation Result")
        self.simulationresult.setFixedSize(450, 300)
        self.simulationresult.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px


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
        self.simulatebutton = QGroupBox("Simulate")
        self.simulatebutton.setFixedSize(450/2, 100)
        self.simulatebutton.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
        self.simulatebutton = QPushButton("Do Simulate")
        self.simulatebutton.clicked.connect(self.dosimulate)
        self.simulatebutton_layout.addWidget(self.simulatebutton)

        self.simulatebutton.setLayout(self.simulatebutton_layout)
        self.horizontal_1_layout.addWidget(self.simulatebutton)


        # =======================
        # make horizontal windget 2
        # =======================
        self.horizontal_2_layout = QHBoxLayout()

        # =======================
        # save as asd button
        # =======================
        self.saveasd_layout = QVBoxLayout()
        self.saveasd = QGroupBox("Save as ASD")
        self.saveasd.setFixedSize(450/2, 100)
        self.saveasd.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px

        self.saveasd.setLayout(self.saveasd_layout)
        self.horizontal_2_layout.addWidget(self.saveasd)

        # =======================
        # save as png button
        # =======================
        self.savepng_layout = QVBoxLayout()
        self.savepng = QGroupBox("Save as PNG")
        self.savepng.setFixedSize(450/2, 100)
        self.savepng.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px

        self.savepng.setLayout(self.savepng_layout)
        self.horizontal_2_layout.addWidget(self.savepng)


        # =======================
        # make horizontal windget 3
        # =======================
        self.horizontal_3_layout = QHBoxLayout()

        # =======================
        # save orientation
        # =======================
        self.saveorientation_layout = QVBoxLayout()
        self.saveorientation = QGroupBox("Save Orientation")
        self.saveorientation.setFixedSize(450/2, 100)
        self.saveorientation.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
        
        self.saveorientation.setLayout(self.saveorientation_layout)
        self.horizontal_3_layout.addWidget(self.saveorientation)

        # =======================
        #Load orientation
        # =======================
        self.loadorientation_layout = QVBoxLayout()
        self.loadorientation = QGroupBox("Load Orientation")
        self.loadorientation.setFixedSize(450/2, 100)
        self.loadorientation.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px

        self.loadorientation.setLayout(self.loadorientation_layout)
        self.horizontal_3_layout.addWidget(self.loadorientation)


        # =======================
        # make horizontal windget 4
        # =======================
        self.horizontal_4_layout = QHBoxLayout()

        # =======================
        # Top view button
        # =======================
        self.topview_layout = QVBoxLayout()
        self.topview = QGroupBox("Top View")
        self.topview.setFixedSize(450/3, 100)
        self.topview.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px

        self.topview.setLayout(self.topview_layout)
        self.horizontal_4_layout.addWidget(self.topview)

        # =======================
        #xz view button
        # =======================
        self.xzview_layout = QVBoxLayout()
        self.xzview = QGroupBox("XZ View")
        self.xzview.setFixedSize(450/3, 100)
        self.xzview.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px

        self.xzview.setLayout(self.xzview_layout)
        self.horizontal_4_layout.addWidget(self.xzview)

        # =======================
        #yz view button
        # =======================
        self.yzview_layout = QVBoxLayout()
        self.yzview = QGroupBox("YZ View")
        self.yzview.setFixedSize(450/3, 100)
        self.yzview.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px

        self.yzview.setLayout(self.yzview_layout)
        self.horizontal_4_layout.addWidget(self.yzview)



        
       

        # =======================
        # Then add the each layout to the main layout
        # =======================
        self.main_layout.addWidget(self.simulationresult)
        self.main_layout.addLayout(self.horizontal_1_layout)
        self.main_layout.addLayout(self.horizontal_2_layout)
        self.main_layout.addLayout(self.horizontal_3_layout)
        self.main_layout.addLayout(self.horizontal_4_layout)

        

        # =======================
        # And finally, set the main layout to the window
        # =======================
        self.setLayout(self.main_layout)

    
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

    #=========================
    # Do tip sample dilation simulation
    #=========================
    def dosimulate(self):
        print("simulate")


#=========================
# display atom coordinate window
#=========================

# class PDBWindow(QtWidgets.QWidget):
#     def __init__(self,parent=None):
#         super(PDBWindow, self).__init__(parent)
#         result = config.get_savedparam("panel", "PDB Display Window")
#         if result is not None:
#           # 一致する行が見つかった場合は、resultを処理する
#             config.panel_left, config.panel_top, config.panel_width, config.panel_height = result
#         else:
#             config.panel_width= 500
#             config.panel_height = 500
#             config.panel_top = 100
#             config.panel_left = 100

#         self.setGeometry(config.panel_left , config.panel_top , config.panel_width, config.panel_height) 

#         self.setWindowTitle("PDB Display Window")

#         self.main_layout = QVBoxLayout()


#         # =======================
#         # pdb diplay window
#         # =======================
#         self.pdbdisplay_layout = QVBoxLayout()
#         self.pdbdisplay = QGroupBox("PDB Display Window")
#         self.pdbdisplay.setFixedSize(450, 300)
#         self.pdbdisplay.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px


#         self.pdbdisplay.setLayout(self.pdbdisplay_layout)

#         # =======================
#         # Then add the each layout to the main layout
#         # =======================
#         self.main_layout.addWidget(self.pdbdisplay)

#         # =======================
#         # And finally, set the main layout to the window
#         # =======================
#         self.setLayout(self.main_layout)





