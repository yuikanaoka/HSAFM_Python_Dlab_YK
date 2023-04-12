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
from PyQt5.QtWidgets import (QWidget, QApplication, QPushButton, QLineEdit,
                             QHBoxLayout, QVBoxLayout, QTextEdit, QProgressBar,
                             QFileDialog, QListView, QAbstractItemView, QComboBox,
                             QDialog, QGridLayout, QHBoxLayout, QHeaderView, QLabel,
                             QProgressDialog, QPushButton, QSizePolicy, QTableWidget,
                             QTableWidgetItem, QSlider, QSpinBox, QToolButton, QStyle,
                             QCheckBox, QGroupBox, QBoxLayout, QMessageBox, QAction,
                             QFileDialog, QMainWindow, QMessageBox, QTextEdit, QMenu, QFrame, QRadioButton, QDoubleSpinBox)

from PyQt5 import QtWidgets

class SettingWindow(QtWidgets.QWidget):

    def __init__(self,parent=None):

        super(SettingWindow, self).__init__(parent)

        self.setGeometry(settingpanel.left, settingpanel.top, settingpanel.width, settingpanel.height)

        self.setWindowTitle("Setting")

        top =10
        left = 30