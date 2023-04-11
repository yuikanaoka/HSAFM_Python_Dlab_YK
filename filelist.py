#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      Uchihashi
#
# Created:     20/02/2018
# Copyright:   (c) Uchihashi 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import sys
import os
from PyQt5.QtCore import pyqtSignal, QMutexLocker, QMutex, QThread


class FileList(QThread):
    ''' store file list'''

    sig_file = pyqtSignal(str)


    def __init__(self, parent=None):
        super(FileList, self).__init__(parent)
        self.stopped = False
        self.mutex = QMutex()

    def setup(self, root_dir, ext):
        self.root_dir = root_dir
        self.ext = ext
        self.retrieve()
        self.stopped = False

        return self.files

    def stop(self):
        with QMutexLocker(self.mutex):
            self.stopped = True

    def run(self):
        for f in self.files:
            fname = f
            self.process_file(fname)
            self.sig_file.emit(fname)   # sginal送信
        self.stop()
        self.finished.emit()        # signal送信

    def retrieve(self):
        ''' root_dirからext拡張子を持つファイルを取得する '''
        self.files = []
        #self.dirs = []
        """for rd, _, fl in os.walk(self.root_dir):
            for f in fl:
                _, fext = os.path.splitext(f)
                if fext == self.ext:
                    self.files.append(os.path.join(rd, f))
        self.length = len(self.files)"""

        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            #print("{0}を検索しています...".format(dirpath))
            for dr in dirnames:
                pass
                #print("{0}というディレクトリがあります".format(dr))
                #print(filenames)
            for file in filenames:
                fext = os.path.splitext(file)
                if fext[1] == self.ext:
                    self.files.append(os.path.join(dirpath, file))
                    #self.files.append(file)
                    #self.files.append(dr)
                    #print("{0}というファイルがあります".format(file))
        #self.files.sort()
        #self.files.sort()
        self.length = len(self.files)
        #result = 1
        ##return self.files
                    #print()  # わかりやすくするための改行、区切り

    def process_file(self, path):
        ''' ひとまず何もしない '''
        cnt = 0
        if os.path.exists(path):
            cnt += 1
        else:
            cnt = 0

    def print(self):
        for f in self.files:
            print(f)


def main(args):
    root_dir = '.'
    ext = '.asd'
    if len(args) == 3:
        root_dir = args[1]
        ext = args[2]
    fileList = FileList()
    fileList.setup(root_dir, ext)
    fileList.print()

if __name__ == '__main__':
    main(sys.argv)
