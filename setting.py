# -------------------------------------------------------------------------------
# Name:        setting.py
# Purpose:
#
# Author:      Uchihashi
#
# Created:     12/4/2023
# Copyright:   (c) Uchihashi 2018
# Licence:     <your licence>
# -------------------------------------------------------------------------------
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFileDialog

from PyQt5 import QtWidgets

import sys

import config  

class SettingWindow(QtWidgets.QWidget):

    def __init__(self,parent=None):

        super(SettingWindow, self).__init__(parent)

        #self.setGeometry(config.settingpanel.left, config.settingpanel.top, config.settingpanel.width, config.settingpanel.height)

        #self.setWindowTitle("Setting")

        #top =10
        #left = 30

        #self.initial_folder_button = QPushButton('Select Folder', self)
        #self.initial_folder_button.move(top, left)
        #self.initial_folder_button.clicked.connect(self.showFileDialog)    

    def initialfolder_setting(self):
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        dirname = QFileDialog.getExistingDirectory(self,
                                                   'open folder',
                                                   config.initialdata_folder,
                                                   QFileDialog.ShowDirsOnly)
        
        if dirname is not None and dirname != "":
            config.initialdata_folder = dirname 

   
# def getPanelSize(self):
#         for widget in QApplication.topLevelWidgets():
#             if isinstance(widget, QWidget):
#                 print(f"Widget: {widget.windowTitle()}")
#                 print(f"Left: {widget.geometry().left()}")
#                 print(f"Top: {widget.geometry().top()}")
#                 print(f"Width: {widget.geometry().width()}")
#                 print(f"Height: {widget.geometry().height()}")

def panel_setting():
    pass
