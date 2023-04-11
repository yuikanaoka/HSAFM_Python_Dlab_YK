#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Uchihashi
#
# Created:     21/02/2018
# Copyright:   (c) Uchihashi 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import sys
import os
import struct
from guimain import FileVariables

class ImageOpen:

    filename = ""

    def __init__(self, filename):
        self.filename = filename
        self.data =""
        fv = FileVariables

    def Open_ImageFile(self):
        print(self.filename)
        #fv =  FileVariables
        with open(self.filename, "rb") as f:
            fv.FileType = struct.unpack('l', f.read(4)) [0]
            print(fv.FileType)
            self.data = struct.unpack('l', f.read(4)) [0]
            self.data = struct.unpack('l', f.read(4)) [0]
            self.data = struct.unpack('l', f.read(4)) [0]
            self.data = struct.unpack('l', f.read(4)) [0]
            print(self.data)
            f.close()