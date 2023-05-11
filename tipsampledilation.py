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
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


import numpy as np
import time
import threading
import datetime

import cv2

from filelist import FileList
from imagefifo import FileImport

from Bio.PDB import PDBParser
import pandas as pd
from PIL import Image


import config
import lineprofile as lp
import removebackground as rb
import noisefilter as nf

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
        self.pixelxdirection = QDoubleSpinBox()
        self.pixelxdirection.setRange(50, 100)
        self.pixelxdirection_layout.addWidget(self.pixelxdirection_label)
        self.pixelxdirection_layout.addWidget(self.pixelxdirection)
        self.pixelxdirection.valueChanged.connect(self.pixelxdirection_change)

        #tip angle
        self.tipangle_layout = QVBoxLayout()  # Create a new QVBoxLayout for the shape
        self.tipangle_label = QLabel("Tip Angle")
        self.tipangle = QDoubleSpinBox()
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
        self.simulationresult.setFixedSize(500, 300)
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
        self.saveasd_layout.addWidget(self.saveasd)
        self.horizontal_2_layout.addLayout(self.saveasd_layout)

        # =======================
        # save as png button
        # =======================
        self.savepng_layout = QVBoxLayout()
        self.savepng = QPushButton("Save as PNG")
        self.savepng.setFixedSize(450/2, 50)
        self.savepng.setStyleSheet("QPushButton { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
        self.savepng_layout.addWidget(self.savepng)
        self.horizontal_2_layout.addLayout(self.savepng_layout)


        # =======================
        # make horizontal windget 3
        # =======================
        self.horizontal_3_layout = QHBoxLayout()

        # =======================
        # save orientation
        # =======================
        self.saveorientation_layout = QVBoxLayout()
        self.saveorientation = QPushButton("Save Orientation")
        self.saveorientation.setFixedSize(450/2, 50)
        self.saveorientation.setStyleSheet("QPushButton { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
        self.saveorientation_layout.addWidget(self.saveorientation)
        self.horizontal_3_layout.addLayout(self.saveorientation_layout)
        

        # =======================
        #Load orientation
        # =======================
        self.loadorientation_layout = QVBoxLayout()
        self.loadorientation = QPushButton("Load Orientation")
        self.loadorientation.setFixedSize(450/2, 50)
        self.loadorientation.setStyleSheet("QPushButton { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
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
        self.topview_layout.addWidget(self.topview)
        self.horizontal_4_layout.addLayout(self.topview_layout)


        # =======================
        #xz view button
        # =======================
        self.xzview_layout = QVBoxLayout()
        self.xzview = QPushButton("XZ View")
        self.xzview.setFixedSize(450/3, 50)
        self.xzview.setStyleSheet("QPushButton { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
        self.xzview_layout.addWidget(self.xzview)
        self.horizontal_4_layout.addLayout(self.xzview_layout)

    
        # =======================
        #yz view button
        # =======================
        self.yzview_layout = QVBoxLayout()
        self.yzview = QPushButton("YZ View")
        self.yzview.setFixedSize(450/3, 50)
        self.yzview.setStyleSheet("QPushButton { font-size: 15px; font-weight: bold; }")  # Set the font size to 20px
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
    # necessary functions for change orientation
    #=========================
    def increment_value(self):
        self.value += self.step_size_spinbox.value()
        print (self.value)

    def decrement_value(self):
        self.value -= self.step_size_spinbox.value()
        print (self.value)
    
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
        if config.atomtype == "C":
            print("carbon")
            config.pdbplot = config.pdbdata[config.pdbdata['Atom Name'].str.startswith('C')]

            config.fig = plt.figure(num="PDB Plot")
            config.ax = config.fig.add_subplot(111, projection='3d')
            config.ax.set_xlabel('X axis')
            config.ax.set_ylabel('Y axis')
            config.ax.set_zlabel('Z axis')
            config.sc=config.ax.scatter(config.pdbplot['X'], config.pdbplot['Y'], config.pdbplot['Z'],color="red")

            plt.show(block=False)

        elif config.atomtype == "N":
            print("nitrogen")
            config.pdbplot = config.pdbdata[config.pdbdata['Atom Name'].str.startswith('N')]
            config.fig = plt.figure(num="PDB Plot")
            config.ax = config.fig.add_subplot(111, projection='3d')
            config.ax.set_xlabel('X axis')
            config.ax.set_ylabel('Y axis')
            config.ax.set_zlabel('Z axis')
            config.sc=config.ax.scatter(config.pdbplot['X'], config.pdbplot['Y'], config.pdbplot['Z'],color="blue")
            plt.show(block=False)

        elif config.atomtype == "O":
            print("oxygen")
            config.pdbplot= config.pdbdata[config.pdbdata['Atom Name'].str.startswith('O')]
            config.fig = plt.figure(num="PDB Plot")
            config.ax = config.fig.add_subplot(111, projection='3d')
            config.ax.set_xlabel('X axis')
            config.ax.set_ylabel('Y axis')
            config.ax.set_zlabel('Z axis')
            config.sc=config.ax.scatter(config.pdbplot['X'], config.pdbplot['Y'], config.pdbplot['Z'],color="green")
            plt.show(block=False)

        elif config.atomtype == "ALL":
            print("all")
            config.fig = plt.figure(num="PDB Plot")
            config.ax = config.fig.add_subplot(111, projection='3d')
            config.ax.set_xlabel('X axis')
            config.ax.set_ylabel('Y axis')
            config.ax.set_zlabel('Z axis')
            config.sc=config.ax.scatter(config.pdbdata['X'], config.pdbdata['Y'], config.pdbdata['Z'],color="black")
            plt.show(block=False)
    
    #=========================
    # atomtype chnaged display update
    #=========================
    def display_atomtype_update(self):
        print ("update")
        if config.atomtype=="C":
            print("carbon")
            config.pdbplot = config.pdbdata[config.pdbdata['Atom Name'].str.startswith('C')]
            config.sc._offsets3d = (config.pdbplot['X'], config.pdbplot['Y'], config.pdbplot['Z'])
            config.sc.set_facecolor("red")
            config.sc.set_edgecolor("red")
            plt.draw()
        elif config.atomtype=="N":
            print("nitrogen")
            config.pdbplot = config.pdbdata[config.pdbdata['Atom Name'].str.startswith('N')]
            config.sc._offsets3d = (config.pdbplot['X'], config.pdbplot['Y'], config.pdbplot['Z'])
            config.sc.set_facecolor("blue")
            config.sc.set_edgecolor("blue")
            plt.draw()
            print (config.pdbplot)
        elif config.atomtype=="O":
            print("oxygen")
            config.pdbplot = config.pdbdata[config.pdbdata['Atom Name'].str.startswith('O')]
            config.sc._offsets3d = (config.pdbplot['X'], config.pdbplot['Y'], config.pdbplot['Z'])
            config.sc.set_facecolor("green")
            config.sc.set_edgecolor("green")
            plt.draw()
        elif config.atomtype=="ALL":
            print("all")
            config.sc._offsets3d = (config.pdbdata['X'], config.pdbdata['Y'], config.pdbdata['Z'])
            config.sc.set_facecolor("black")
            config.sc.set_edgecolor("black")
            plt.draw()
    


    #=========================
    # Do tip sample dilation simulation
    #=========================
    def dosimulate(self):
        print("simulate")
        #self.createtip()
        #one pixel dilation
        self.dilation()
        #final dilation




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
    # create tip
    #=========================
    def createtip(self):
        print("create tip")
        

        z_off = (config.tipradius / 2) / math.tan(config.tipangle * math.pi / 180) ** 2
        r_crit=config.tipradius/math.tan(config.tipangle*math.pi/180)
        z_crit=r_crit/math.tan(config.tipangle*math.pi/180)-z_off

        if config.tipshape=="Paraboloid":
            i_xm=(1/config.dx)*math.sqrt(2*config.tipradius*(config.zcoordinate.max()-config.zcoordinate.min()))
            config.tipsize=2*math.ceil(i_xm)+1
            print ("paraboloid")
        
        elif config.tipshape=="Cone":
            r_crit=config.tipradius/math.sqrt(1+math.tan(config.tipangle*math.pi/180)**2)
            z_crit=r_crit*math.tan(config.tipangle*math.pi/180)-z_off
            z_off=-config.tipradius+math.sqrt(config.tipradius**2-r_crit**2)+r_crit**2/math.sqrt(config.tipradius**2-r_crit**2)
            if z_crit>config.zcoordinate.max():
                i_xm=(1/config.dx)*math.sqrt(config.tipradius**2-(config.tipradius-(config.zcoordinate.max()-config.zcoordinate.min()))**2)
            else:
                i_xm=(1/config.dx)*((config.zcoordinate.max()-config.zcoordinate.min())+z_off)*math.tan(config.tipangle*math.pi/180)
            config.tipsize=2*math.ceil(i_xm)+1
        
                             
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
                    

        
        #print (config.tipwave)
        print (config.tipsize)
        print (config.tipwave.shape)
        print (type(config.tipwave))
        tipwavex,tipwavey=np.indices(config.tipwave.shape)

        
        figtip=plt.figure(num="Tip")
        oneax=figtip.add_subplot(111, projection='3d')
        oneax.plot_surface(tipwavex,tipwavey,config.tipwave)
        #plt.imshow(config.tipwave)
        plt.show(block=False)
        plt.draw()

        

        

    #=========================
    # one pixel dilation
    #=========================
    def onepixeldilation(self):
        print ("one pixel dilation")
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
        
        onepixelx, onepixely=np.indices(config.onepixeldilation.shape)
        figonepixel=plt.figure(num="onepixel")
        oneax=figonepixel.add_subplot(111, projection='3d')
        oneax.scatter(onepixelx,onepixely,config.onepixeldilation)
        oneax.set_xlabel('X axis')
        oneax.set_ylabel('Y axis')
        oneax.set_zlabel('Z axis')
        plt.show(block=False)
        plt.draw()

        img_array=(config.onepixeldilation/config.onepixeldilation.max())*255
        img_array=img_array.astype(np.uint8)
        #img=Image.fromarray(img_array)
        #img.save('dilation.png')
        imgone=plt.figure(num="Simlated one pixel img")
        imgax=imgone.add_subplot(111)
        imgax.imshow(img_array)
        plt.show(block=False)


    
    #=========================
    # make dilation
    #=========================
    def dilation(self):
        config.xcoordinate=config.pdbplot['X']-config.pdbplot['X'].min()
        config.ycoordinate=config.pdbplot['Y']-config.pdbplot['Y'].min()
        config.zcoordinate=config.pdbplot['Z']-config.pdbplot['Z'].min()

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
        print("after create tip")
        print (config.tipsize)
        print (config.tipwave.shape)

        l_x=config.grid_sizex+2*config.tipsize
        l_y=config.grid_sizey+2*config.tipsize
        config.dilationborder=np.zeros((l_x,l_y))
        config.dilationborder[config.tipsize:l_x-config.tipsize,config.tipsize:l_y-config.tipsize]=config.onepixeldilation
        img_array_border=(config.dilationborder/config.dilationborder.max())*255
        img_array_border=img_array_border.astype(np.uint8)
        #img=Image.fromarray(img_array)
        #img.save('dilation.png')
        imgborderfig=plt.figure(num="dilation border img")
        imgborderax=imgborderfig.add_subplot(111)
        imgborderax.imshow(img_array_border)
        plt.show(block=False)

        config.dilation=np.zeros((l_x,l_y))
        print (l_x)
        print (l_y)


        #make dilation
        for ix in range(0,l_x-config.tipwave.shape[0]):
            for iy in range(0,l_y-config.tipwave.shape[1]):
                #print (iy)
                #print (iy+config.tipsize)

                #print(ix)
                # print(ix+config.tipsize)
                z_diffmap=config.dilationborder[ix:ix+config.tipsize,iy:iy+config.tipsize]-config.tipwave
                # print ("ok")
                # print(z_diffmap.shape)
                # print ("======")
                displacement=z_diffmap.max()
                config.dilation[ix][iy]=displacement
        
        #config.dilation=config.dilation/(config.dilation.max())
        print ("type")
        print(type(config.dilation))
        config.dilation=config.dilation/10
        np.savetxt('dilation.csv', config.dilation, delimiter=',')

        #apply afm color map and save image 
        #self.makeDIcolor()
        #config.dilation_img=cv2.applyColorMap(config.dilation, config.DIcolor)
        img_array=(config.dilation/config.dilation.max())*255
        img_array=img_array.astype(np.uint8)
        #img=Image.fromarray(img_array)
        #img.save('dilation.png')
        imgdilationfig=plt.figure(num="Simlated img")
        imgax=imgdilationfig.add_subplot(111)
        imgax.imshow(img_array)
        plt.show(block=False)




        dilationx, dilationy=np.indices(config.dilation.shape)
        figdilation=plt.figure(num="dilation")
        dilaax=figdilation.add_subplot(111, projection='3d')
        dilaax.scatter(dilationx,dilationy,config.dilation)
        dilaax.set_xlabel('X axis')
        dilaax.set_ylabel('Y axis')
        dilaax.set_zlabel('Z axis')
        plt.show(block=False)
        plt.draw()

    #=========================
    # make color map
    #=========================
    def makeDIcolor(self):

        for i in range(0, 255):

            if (i < 158):
                config.DIcolor[i, 0, 2] = i / 157 * 255
            elif (i >= 158):
                config.DIcolor[i, 0, 2] = 255

            config.DIcolor[i, 0, 1] = i

            if (i < 176):
                config.DIcolor[i, 0, 0] = 0
            elif (i >= 176):
                config.DIcolor[i, 0, 0] = 67 + 188 * (i - 176) / 79



        






        

        
    

    
 


