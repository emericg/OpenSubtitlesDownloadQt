#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# OpenSubtitlesDownloadQt.py / Version 5.0
# This software is designed to help you find and download subtitles for your favorite videos!

# You can browse the official website:
# https://emericg.github.io/OpenSubtitlesDownloadQt
# You can browse the project's GitHub page:
# https://github.com/emericg/OpenSubtitlesDownloadQt
# Learn much more about OpenSubtitlesDownloadQt.py on its wiki:
# https://github.com/emericg/OpenSubtitlesDownloadQt/wiki

# Copyright (c) 2018 by Emeric GRANGE <emeric.grange@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Contributors / special thanks:
# LenuX for his work on the Qt GUI
# jeroenvdw for his work on the 'subtitles automatic selection' and the 'search by filename'
# Gui13 for his work on the arguments parsing
# Tomáš Hnyk <tomashnyk@gmail.com> for his work on the 'multiple language' feature
# Carlos Acedo <carlos@linux-labs.net> for his work on the original script

import sys
if sys.version_info <= (3,0):
    print("Python 3 is not available on your system, exiting...")
    sys.exit(2)

try:
    from PyQt5 import QtCore, QtGui, QtWidgets
except ImportError:
    print("PyQt5 is not available on your system, exiting...")
    sys.exit(2)

import os
import re
import struct
import mimetypes
import subprocess
import argparse
import time
import gzip
import shutil
import urllib.request
from xmlrpc.client import ServerProxy, Error
import configparser

# ==== Opensubtitles.org server settings =======================================

# XML-RPC server domain for opensubtitles.org:
osd_server = ServerProxy('http://api.opensubtitles.org/xml-rpc')

# You can use your opensubtitles.org account to avoid "in-subtitles" advertisment and bypass download limits
# Be careful about your password security, it will be stored right here in plain text...
# You can also change opensubtitles.org language, it will be used for error codes and stuff
osd_username = ''
osd_password = ''
osd_language = 'en'

# ==== Language settings =======================================================

# Write 2-letter language code (ex: _en) at the end of the subtitles file, separated by the following character.
opt_language_separator = '_'

# ==== Search settings =========================================================

# If the search by movie hash fails, search by file name will be used as backup.
opt_search_byname = 'on'

# Search and download a subtitles even if a subtitles file already exists.
opt_search_overwrite = 'on'

# ==== Exit codes ==============================================================
# 0: Success and subtitles downloaded
# 1: Success but no subtitles found
# 2: Failure

# ==== Super Print =============================================================
# priority: info, warning, error
# title: box title
# message: full text, with tags and breaks

def superPrint(priority, title, message):
    """Print messages through Qt interface"""
    message = message.replace("\n", "<br>")
    alert = QtWidgets.QMessageBox()
    alert.setWindowTitle(title)
    alert.setWindowIcon(QtGui.QIcon.fromTheme("document-properties"))
    alert.setText(message)
    alert.exec_()

# ==== QT Settings Management Window ===========================================
# If config file does not exists create it, put the default values and print the
# settings window, then get the values and write the config file.
#
# If config file does exists parse it and get the values.

subLang=[("Arabic","ara"),("Bengali","ben"),("Cantonese","yue"),("Dutch","nld"),("English","eng"),("Filipino","fil"),("French","fre"),("German","ger"),("Hindi","hin"),("Indonesian","ind"),("Italian","ita"),("Japanese","jpn"),("Korean","kor"),("Mandarin","mdr"),("Persian","per"),("Portuguese","por"),("Russian","rus"),("Spanish","spa"),("Swahili","swa"),("Turkish","tur"),("Vietnamese","vie")]


class settingsWindow(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(settingsWindow,self).__init__(parent)
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('OpenSubtitlesDownload  Settings ')
        self.setWindowIcon(QtGui.QIcon.fromTheme("document-properties"))

        titleFont = QtGui.QFont()
        titleFont.setBold(True)
        titleFont.setUnderline(True)

        # Languages selection gui (puchbuttons)
        self.langLabel = QtWidgets.QLabel("1/ Select the language(s) you need:")
        self.langLabel.setFont(titleFont)

        # Preferences selection gui (comboboxes)
        self.prefLabel = QtWidgets.QLabel("2/ Select your preferences:")
        self.prefLabel.setFont(titleFont)
        self.optLabel = QtWidgets.QLabel("Write 2-letter language code (ex: _en) at the end of the subtitles file?")
        self.optBox = QtWidgets.QComboBox()
        self.optBox.setMaximumWidth(100)
        self.optBox.addItems(['auto','on','off'])
        self.modeLabel = QtWidgets.QLabel("Subtitles selection mode:")
        self.modeBox = QtWidgets.QComboBox()
        self.modeBox.setMaximumWidth(100)
        self.modeBox.addItems(['manual','auto'])

        # Columns in selection window (checkboxes)
        self.columnLabel = QtWidgets.QLabel("3/ Select the colums to show in the selection window:")
        self.columnLabel.setFont(titleFont)
        self.langBox = QtWidgets.QCheckBox("Subtitles language")
        self.hiBox = QtWidgets.QCheckBox("Hearing impaired version")
        self.rateBox = QtWidgets.QCheckBox("Users rating")
        self.countBox = QtWidgets.QCheckBox("Downloads count")

        # Help / Link to the wiki
        self.helpLabel = QtWidgets.QLabel("If you have any troubles: <a href=https://github.com/emericg/OpenSubtitlesDownloadQt/wiki> Visit the wiki!</a> ")
        self.helpLabel.setOpenExternalLinks(True)

        # Finish button and its function
        self.finishButton = QtWidgets.QPushButton("Finish",self)
        self.finishButton.clicked.connect(self.doFinish)

        self.vbox = QtWidgets.QVBoxLayout()    # Main vertical layout
        self.grid = QtWidgets.QGridLayout()    # Grid layout for the languages buttons

        # Language section:
        self.vbox.addWidget(self.langLabel)
        self.vbox.addSpacing(30)

        # Create the buttons for languages from the list and add them to the layout
        x=0
        y=0
        self.pushLang=[]
        for i in range(0,len(subLang)):
           self.pushLang.append(QtWidgets.QPushButton(subLang[i][0],self))
           self.pushLang[i].setCheckable(True)
           self.grid.addWidget(self.pushLang[i],x,y)
           y=(y+1)%3 # Coz we want 3 columns
           if y==0: x+=1

        self.vbox.addLayout(self.grid)

        # Add the other widgets to the layout vertical
        self.vbox.addSpacing(20)
        self.vbox.addWidget(self.prefLabel)
        self.vbox.addWidget(self.optLabel)
        self.vbox.addWidget(self.optBox)
        self.vbox.addWidget(self.modeLabel)
        self.vbox.addWidget(self.modeBox)
        self.vbox.addSpacing(30)
        self.vbox.addWidget(self.columnLabel)
        self.vbox.addWidget(self.langBox)
        self.vbox.addWidget(self.hiBox)
        self.vbox.addWidget(self.rateBox)
        self.vbox.addWidget(self.countBox)
        self.vbox.addSpacing(20)
        self.vbox.addWidget(self.helpLabel)
        self.vbox.addWidget(self.finishButton)

        self.setLayout(self.vbox)

    def doFinish(self):
        global opt_languages,opt_language_suffix, opt_search_mode, opt_selection_language, opt_selection_hi, opt_selection_rating, opt_selection_count
        opt_languages = []

        # Get the values of the comboboxes and put them in the global ones:
        opt_language_suffix = self.optBox.currentText()
        opt_search_mode = self.modeBox.currentText()

        # Same for the checkboxes:
        opt_selection_language='off'
        opt_selection_hi='off'
        opt_selection_rating='off'
        opt_selection_count='off'
        if self.langBox.isChecked(): opt_selection_language='on'
        if self.hiBox.isChecked(): opt_selection_hi='on'
        if self.rateBox.isChecked(): opt_selection_rating='on'
        if self.countBox.isChecked(): opt_selection_count='on'

        # Get all the selected languages and construct the IDsList:
        check = 0
        for i in range(0, len(subLang)):
            if self.pushLang[i].isChecked():
                opt_languages.append(subLang[i][1])
                check = 1

        # Close the window when its all saved (and if at least one lang is selected)
        if check == 1:
            self.close()
        else:
            superPrint(self,self.windowTitle(),"Cannot save with those settings: choose at least one language please")

def configQt(calledManually):
    global opt_languages, opt_language_suffix, opt_search_mode, opt_selection_language, opt_selection_hi, opt_selection_rating, opt_selection_count
    # Try to get the xdg folder for the config file, if not we use $HOME/.config
    if os.getenv("XDG_CONFIG_HOME"):
        confdir = os.path.join (os.getenv("XDG_CONFIG_HOME"), "OpenSubtitlesDownload")
        confpath = os.path.join (confdir, "OpenSubtitlesDownload.conf")
    else:
        confdir = os.path.join (os.getenv("HOME"), ".config/OpenSubtitlesDownload/")
        confpath = os.path.join (confdir, "OpenSubtitlesDownload.conf")

    confparser = configparser.SafeConfigParser()

    if not os.path.isfile(confpath) or calledManually:
        # Create the conf folder if it doesn't exist:
        try:
            os.stat(confdir)
        except:
            os.mkdir(confdir)

        # Print the settings window:
        gui = settingsWindow()
        gui.exec_()

        # Write the conf file with the parser:
        confparser.add_section('languagesIDs')
        i = 0
        for ids in opt_languages:
            confparser.set ('languagesIDs', 'sublanguageids'+str(i),ids)
            i+=1

        confparser.add_section('settings')
        confparser.set ('settings', 'opt_language_suffix', str(opt_language_suffix))
        confparser.set ('settings', 'opt_search_mode', str(opt_search_mode))
        confparser.set ('settings', 'opt_selection_language', str(opt_selection_language))
        confparser.set ('settings', 'opt_selection_hi', str(opt_selection_hi))
        confparser.set ('settings', 'opt_selection_rating', str(opt_selection_rating))
        confparser.set ('settings', 'opt_selection_count', str(opt_selection_count))

        with open(confpath, 'w') as confile:
            confparser.write(confile)

    # If the file is already there we get the values:
    else:
        confparser.read(confpath)
        opt_languages=[]
        languages = ""
        for i in range(0,len(confparser.items('languagesIDs'))):
            languages += confparser.get('languagesIDs', 'sublanguageids'+str(i)) + ","
        opt_languages.append(languages)
        opt_language_suffix = confparser.get ('settings', 'opt_language_suffix')
        opt_search_mode = confparser.get ('settings', 'opt_search_mode')
        opt_selection_language = confparser.get ('settings', 'opt_selection_language')
        opt_selection_hi = confparser.get ('settings', 'opt_selection_hi')
        opt_selection_rating = confparser.get ('settings', 'opt_selection_rating')
        opt_selection_count = confparser.get ('settings', 'opt_selection_count')


# ==== Check file path & type ==================================================

def checkFileValidity(path):
    """Check mimetype and/or file extension to detect valid video file"""
    if os.path.isfile(path) == False:
        superPrint("error", "File type error!", "This is not a file:\n<i>" + path + "</i>")
        return False

    fileMimeType, encoding = mimetypes.guess_type(path)
    if fileMimeType == None:
        fileExtension = path.rsplit('.', 1)
        if fileExtension[1] not in ['avi', 'mp4', 'mov', 'mkv', 'mk3d', 'webm', \
                                    'ts', 'mts', 'm2ts', 'ps', 'vob', 'evo', 'mpeg', 'mpg', \
                                    'm1v', 'm2p', 'm2v', 'm4v', 'movhd', 'movx', 'qt', \
                                    'mxf', 'ogg', 'ogm', 'ogv', 'rm', 'rmvb', 'flv', 'swf', \
                                    'asf', 'wm', 'wmv', 'wmx', 'divx', 'x264', 'xvid']:
            superPrint("error", "File type error!", "This file is not a video (unknown mimetype AND invalid file extension):\n<i>" + path + "</i>")
            return False
    else:
        fileMimeType = fileMimeType.split('/', 1)
        if fileMimeType[0] != 'video':
            superPrint("error", "File type error!", "This file is not a video (unknown mimetype):\n<i>" + path + "</i>")
            return False

    return True

# ==== Check for existing subtitles file =======================================

def checkSubtitlesExists(path):
    """Check if a subtitles already exists for the current file"""

    for ext in ['srt', 'sub', 'sbv', 'smi', 'ssa', 'ass', 'usf']:
        subPath = path.rsplit('.', 1)[0] + '.' + ext
        if os.path.isfile(subPath) == True:
            superPrint("info", "Subtitles already downloaded!", "A subtitles file already exists for this file:\n<i>" + subPath + "</i>")
            return True
        # With language code? Only check the first language (and probably using the wrong language suffix format)
        if ((opt_language_suffix == 'on') or (opt_language_suffix == 'auto')):
            if len(opt_languages) == 1:
                splitted_languages_list = opt_languages[0].split(',')
            else:
                splitted_languages_list = opt_languages
            subPath = path.rsplit('.', 1)[0] + opt_language_separator + splitted_languages_list[0] + '.' + ext
            if os.path.isfile(subPath) == True:
                superPrint("info", "Subtitles already downloaded!", "A subtitles file already exists for this file:\n<i>" + subPath + "</i>")
                return True

    return False

# ==== Hashing algorithm =======================================================
# Info: http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
# This particular implementation is coming from SubDownloader: http://subdownloader.net/

def hashFile(path):
    """Produce a hash for a video file: size + 64bit chksum of the first and
    last 64k (even if they overlap because the file is smaller than 128k)"""
    try:
        longlongformat = 'Q' # unsigned long long little endian
        bytesize = struct.calcsize(longlongformat)
        format = "<%d%s" % (65536//bytesize, longlongformat)

        f = open(path, "rb")

        filesize = os.fstat(f.fileno()).st_size
        hash = filesize

        if filesize < 65536 * 2:
            superPrint("error", "File size error!", "File size error while generating hash for this file:\n<i>" + path + "</i>")
            return "SizeError"

        buffer = f.read(65536)
        longlongs = struct.unpack(format, buffer)
        hash += sum(longlongs)

        f.seek(-65536, os.SEEK_END) # size is always > 131072
        buffer = f.read(65536)
        longlongs = struct.unpack(format, buffer)
        hash += sum(longlongs)
        hash &= 0xFFFFFFFFFFFFFFFF

        f.close()
        returnedhash = "%016x" % hash
        return returnedhash

    except IOError:
        superPrint("error", "I/O error!", "Input/Output error while generating hash for this file:\n<i>" + path + "</i>")
        return "IOError"

# ==== Qt subs window: Cross platform subtitles selection window ===============

class subsWindow(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(subsWindow,self).__init__(parent)
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('OpenSubtitlesDownload: Choose you subtitle')
        self.setWindowIcon(QtGui.QIcon.fromTheme("document-properties"))
        self.resize(720, 320)

        self.vBox = QtWidgets.QVBoxLayout()    # Main vertical layout

        # Title and filename of the video , each in a horizontal layout
        labelFont = QtGui.QFont()
        labelFont.setBold(True)
        self.titleTxtLabel = QtWidgets.QLabel("Title: ")
        self.titleTxtLabel.setFont(labelFont)
        self.titleLabel = QtWidgets.QLabel(videoTitle.replace("\\", ""))
        self.titleHBox = QtWidgets.QHBoxLayout()
        self.titleHBox.addWidget(self.titleTxtLabel)
        self.titleHBox.addWidget(self.titleLabel)
        self.titleHBox.addStretch(1)

        self.nameTxtLabel = QtWidgets.QLabel("Filename: ")
        self.nameTxtLabel.setFont(labelFont)
        self.nameLabel = QtWidgets.QLabel(videoFileName)
        self.nameHBox = QtWidgets.QHBoxLayout()
        self.nameHBox.addWidget(self.nameTxtLabel)
        self.nameHBox.addWidget(self.nameLabel)
        self.nameHBox.addStretch(1)

        # Table containing the list of the subtitles:
        self.subTable = QtWidgets.QTableWidget()
        self.subTable.setShowGrid(False)   # Don't show the table grid
        self.subTable.setSelectionBehavior(1) # 1 = QAbstractItemView::SelectRows, selecting only rows 
        self.subTable.verticalHeader().setVisible(False)  # Don't print the lines number

        ## Set col and lines nunbers depending on on the user's choices and the number of item in the list
        self.hLabels = "Available subtitles (synchronized)"
        self.colCount = 1

        # Build the colums an their labels, depending on the user's choices
        if opt_selection_language == "on":
            self.hLabels += ";Language"
            self.colCount += 1

        if opt_selection_hi == "on":
            self.hLabels += ";HI"
            self.colCount += 1

        if opt_selection_rating == "on":
            self.hLabels += ";Rating"
            self.colCount += 1

        if opt_selection_count == "on":
            self.hLabels += ";Downloads"
            self.colCount += 1

        self.subTable.setColumnCount(self.colCount)
        self.subTable.setHorizontalHeaderLabels(self.hLabels.split(";"))
        self.subTable.setRowCount(len(subtitlesList['data']))

        # Set the content of the table:
        rowIndex = 0

        for sub in subtitlesList['data']:
            colIndex = 0
            item = QtWidgets.QTableWidgetItem(sub['SubFileName'])
            item.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable)  # Flags to disable editing of the cells
            self.subTable.setItem(rowIndex,colIndex, item)
            self.subTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch) # Stretch the first column

            if opt_selection_language == "on":
                colIndex += 1
                item = QtWidgets.QTableWidgetItem(sub['LanguageName'])
                item.setTextAlignment(0x0084) # Center the content of the cell
                item.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable)
                self.subTable.setItem(rowIndex,colIndex, item)

            if opt_selection_hi == 'on':
                colIndex += 1
                if sub['SubHearingImpaired'] == '1':
                    item = QtWidgets.QTableWidgetItem(u'\u2713')
                    self.subTable.setItem(rowIndex,colIndex, item)
                item.setTextAlignment(0x0084)
                item.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable)

            if opt_selection_rating == "on":
                colIndex += 1
                item = QtWidgets.QTableWidgetItem(sub['SubRating'])
                item.setTextAlignment(0x0084)
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                item.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable)
                self.subTable.setItem(rowIndex,colIndex, item)

            if opt_selection_count == "on":
                colIndex += 1
                item = QtWidgets.QTableWidgetItem(sub['SubDownloadsCnt'])
                item.setTextAlignment(0x0084)
                item.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable)
                self.subTable.setItem(rowIndex,colIndex, item)

            rowIndex += 1 # Next row
        self.subTable.selectRow(0) # select the first row by default

        # Create the buttons and connect them to the right function
        self.settingsButton = QtWidgets.QPushButton("Settings",self)
        self.settingsButton.clicked.connect(self.doConfig)
        self.cancelButton = QtWidgets.QPushButton("Cancel",self)
        self.cancelButton.clicked.connect(self.doCancel)
        self.okButton = QtWidgets.QPushButton("Accept",self)
        self.okButton.setDefault(True)
        self.okButton.clicked.connect(self.doAccept)

        # Handle double click on the selected sub
        self.subTable.doubleClicked.connect(self.doAccept)

        # Put the bottom buttons in a H layout, Cancel and validate buttons are pushed to the bottom right corner
        self.buttonHBox = QtWidgets.QHBoxLayout()
        self.buttonHBox.addWidget(self.settingsButton)
        self.buttonHBox.addStretch(1)
        self.buttonHBox.addWidget(self.cancelButton)
        self.buttonHBox.addWidget(self.okButton)

        # Put the differents layouts in the main vertical one
        self.vBox.addLayout(self.titleHBox)
        self.vBox.addLayout(self.nameHBox)
        self.vBox.addWidget(self.subTable)
        self.vBox.addLayout(self.buttonHBox)
        self.setLayout(self.vBox)

        self.next = False # Variable to know if we continue the script after this window

    def doCancel(self):
        self.close()

    def doAccept(self):
        self.next = True
        self.selectedSub = str(self.subTable.item(self.subTable.currentRow(),0).text())
        self.close()

    def doConfig(self):
        configQt(True)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape: # For escape button
            sys.exit(0)

    def closeEvent(self,event):
        if not self.next: # If not "Accept" clicked..
            sys.exit(0)

def selectionQt(subtitlesList):
    gui = subsWindow()
    gui.exec_()
    return gui.selectedSub


# ==== Qt download window, thread and function =================================

class downloadWindow(QtWidgets.QDialog):
    def __init__(self,subtitleURL,subtitlePath,parent=None):
        super(downloadWindow,self).__init__(parent)
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('OpenSubtitlesDownload: Downloading ...')
        self.setWindowIcon(QtGui.QIcon.fromTheme("document-properties"))
        self.resize(380,90)

        # Create a progress bar and a label, add them to the main vertical layout
        self.vBox = QtWidgets.QVBoxLayout()
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setRange(0,0)
        self.vBox.addWidget(self.progressBar)
        self.label = QtWidgets.QLabel("Please wait while the subtitles are being downloaded")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.vBox.addWidget(self.label)
        self.setLayout(self.vBox)

        def onFinished():
            self.progressBar.setRange(0,1)
            self.close()

        # Initiate the dowloading task in a thread
        self.task = downloadThread(subtitleURL, subtitlePath)
        self.task.finished.connect(onFinished)
        self.task.start()

# Thread for downloading the sub and when done emit the signal to close the window
class downloadThread(QtCore.QThread):
    def __init__(self, subtitleURL, subtitlePath, parent=None):
        super(downloadThread,self).__init__(parent)
        finished = QtCore.pyqtSignal()
        self.subURL = subtitleURL
        self.subPath = subtitlePath

    def run(self):
        file_name, headers = urllib.request.urlretrieve(self.subURL)
        tmpFile = gzip.GzipFile(file_name)
        open(self.subPath, 'wb').write(tmpFile.read())
        self.finished.emit()

def downloadQt(subtitleURL,subtitlePath):
    gui = downloadWindow(subtitleURL,subtitlePath)
    gui.exec_()

    if os.path.isfile(subtitlePath):
        return 0
    else:
        return 1

# ==== Automatic selection mode ================================================

def selectionAuto(subtitlesList):
    """Automatic subtitles selection using filename match"""

    videoFileParts = videoFileName.replace('-','.').replace(' ','.').replace('_','.').lower().split('.')
    maxScore = -1

    for subtitle in subtitlesList['data']:
        subFileParts = subtitle['SubFileName'].replace('-','.').replace(' ','.').replace('_','.').lower().split('.');
        score = 0
        if subtitle['MatchedBy'] == 'moviehash':
            score = score + 1 # extra point if the sub is found by hash, which is the preferred way to find subs
        for subPart in subFileParts:
            for filePart in videoFileParts:
                if subPart == filePart:
                    score = score + 1
        if score > maxScore:
            maxScore = score
            subtitlesSelected = subtitle['SubFileName']

    return subtitlesSelected


# ==== Main program (execution starts here) ====================================
# ==============================================================================

ExitCode = 2
Application = QtWidgets.QApplication(sys.argv)

# Get OpenSubtitlesDownloadQt.py script path
execPath = str(sys.argv[0])

# ==== Get valid video paths
videoPathList = []

# No filePathListArg from the arg parser? Try selected file(s) from nautilus environment variables:
# $NAUTILUS_SCRIPT_SELECTED_FILE_PATHS (only for local storage)
# $NAUTILUS_SCRIPT_SELECTED_URIS
# Try to get file(s) provided by nautilus
filePathListEnv = os.environ.get('NAUTILUS_SCRIPT_SELECTED_URIS')

try: 

    if filePathListEnv != None:
        # Check file(s) type and validity
        for filePath in filePathListEnv.splitlines():
            # Work a little bit of magic (Make sure we have a clean and absolute path, even from an URI)
            filePath = os.path.abspath(os.path.basename(filePath))
            filePath = urllib.request.url2pathname(filePath)
            if checkFileValidity(filePath):
                videoPathList.append(filePath)

    # Check if the subtitles exists videoPathList
    if opt_search_overwrite == 'off':
        for videoPathDispatch in videoPathList:
            if checkSubtitlesExists(videoPathDispatch) == True:
                videoPathList.remove(videoPathDispatch)

        # If videoPathList is empty, exit!
        if len(videoPathList) == 0:
            sys.exit(1)

    # ==== Automatic configuration window 
    configQt(False)

    # ==== Connection
    try:
        # Connection to opensubtitles.org server
        session = osd_server.LogIn(osd_username, osd_password, osd_language, 'opensubtitles-download 5.0')
    except Exception:
        # Retry once, it could be a momentary overloaded server?
        time.sleep(3)
        try:
            # Connection to opensubtitles.org server
            session = osd_server.LogIn(osd_username, osd_password, osd_language, 'opensubtitles-download 5.0')
        except Exception:
            # Failed connection attempts?
            superPrint("error", "Connection error!", "Unable to reach opensubtitles.org servers!\n\nPlease check:\n- Your Internet connection status\n- www.opensubtitles.org availability\n- Your downloads limit (200 subtitles per 24h)\nThe subtitles search and download service is powered by opensubtitles.org. Be sure to donate if you appreciate the service provided!")
            sys.exit(2)

    # Connection refused?
    if session['status'] != '200 OK':
        superPrint("error", "Connection error!", "Opensubtitles.org servers refused the connection: " + session['status'] + ".\n\nPlease check:\n- Your Internet connection status\n- www.opensubtitles.org availability\n- Your 200 downloads per 24h limit")
        sys.exit(2)

    # ==== Search and download subtitles
    for videoPath in videoPathList:

        searchLanguage = 0
        searchLanguageResult = 0
        videoTitle = 'Unknown video title'
        videoHash = hashFile(videoPath)
        videoSize = os.path.getsize(videoPath)
        videoFileName = os.path.basename(videoPath)

        # Count languages marked for this search
        for SubLanguageID in opt_languages:
            searchLanguage += len(SubLanguageID.split(','))

        searchResultPerLanguage = [searchLanguage]

        # ==== Search for available subtitles using file hash and size
        for SubLanguageID in opt_languages:
            searchList = []
            searchList.append({'sublanguageid':SubLanguageID, 'moviehash':videoHash, 'moviebytesize':str(videoSize)})
            try:
                subtitlesList = osd_server.SearchSubtitles(session['token'], searchList)
            except Exception:
                # Retry once, we are already connected, the server is probably momentary overloaded
                time.sleep(3)
                try:
                    subtitlesList = osd_server.SearchSubtitles(session['token'], searchList)
                except Exception:
                    superPrint("error", "Search error!", "Unable to reach opensubtitles.org servers!\n<b>Search error</b>")

            # No results using search by hash? Retry with filename
            if (not subtitlesList['data']) and (opt_search_byname == 'on'):
                searchList = []
                searchList.append({'sublanguageid':SubLanguageID, 'query':videoFileName})
                try:
                    subtitlesList = osd_server.SearchSubtitles(session['token'], searchList)
                except Exception:
                    # Retry once, we are already connected, the server is probably momentary overloaded
                    time.sleep(3)
                    try:
                        subtitlesList = osd_server.SearchSubtitles(session['token'], searchList)
                    except Exception:
                        superPrint("error", "Search error!", "Unable to reach opensubtitles.org servers!\n<b>Search error</b>")

            # Parse the results of the XML-RPC query
            if subtitlesList['data']:

                # Mark search as successful
                searchLanguageResult += 1
                subtitlesSelected = ''

                # If there is only one subtitles, auto-select it (only when matched by file hash)
                if (len(subtitlesList['data']) == 1) and (subtitlesList['data'][0]['MatchedBy'] == 'moviehash'):
                    subtitlesSelected = subtitlesList['data'][0]['SubFileName']

                # Get video title
                videoTitle = subtitlesList['data'][0]['MovieName']

                # Title and filename may need string sanitizing to avoid dialog handling errors
                videoTitle = videoTitle.replace('"', '\\"')
                videoTitle = videoTitle.replace("'", "\'")
                videoTitle = videoTitle.replace('`', '\`')
                videoTitle = videoTitle.replace("&", "&amp;")
                videoFileName = videoFileName.replace('"', '\\"')
                videoFileName = videoFileName.replace("'", "\'")
                videoFileName = videoFileName.replace('`', '\`')
                videoFileName = videoFileName.replace("&", "&amp;")

                # If there is more than one subtitles and opt_search_mode != 'auto',
                # then let the user decide which one will be downloaded
                if subtitlesSelected == '':
                    # Automatic subtitles selection?
                    if opt_search_mode == 'auto':
                        subtitlesSelected = selectionAuto(subtitlesList)
                    else:
                        # Go through the list of subtitles and handle 'auto' settings activation
                        for item in subtitlesList['data']:
                            if opt_selection_language == 'auto':
                                if searchLanguage > 1:
                                    opt_selection_language = 'on'
                            if opt_selection_hi == 'auto':
                                if item['SubHearingImpaired'] == '1':
                                    opt_selection_hi = 'on'
                            if opt_selection_rating == 'auto':
                                if item['SubRating'] != '0.0':
                                    opt_selection_rating = 'on'
                            if opt_selection_count == 'auto':
                                opt_selection_count = 'on'

                        # Spawn selection window :
                        subtitlesSelected = selectionQt(subtitlesList)

                # If a subtitles has been selected at this point, download it!
                if subtitlesSelected:
                    subIndex = 0
                    subIndexTemp = 0

                    # Select the subtitles file to download
                    for item in subtitlesList['data']:
                        if item['SubFileName'] == subtitlesSelected:
                            subIndex = subIndexTemp
                            break
                        else:
                            subIndexTemp += 1

                    subLangId = opt_language_separator  + subtitlesList['data'][subIndex]['ISO639']
                    subLangName = subtitlesList['data'][subIndex]['LanguageName']
                    subURL = subtitlesList['data'][subIndex]['SubDownloadLink']
                    subPath = videoPath.rsplit('.', 1)[0] + '.' + subtitlesList['data'][subIndex]['SubFormat']

                    # Write language code into the filename?
                    if ((opt_language_suffix == 'on') or
                        (opt_language_suffix == 'auto' and searchLanguageResult > 1)):
                        subPath = videoPath.rsplit('.', 1)[0] + subLangId + '.' + subtitlesList['data'][subIndex]['SubFormat']

                    # Escape non-alphanumeric characters from the subtitles path
                    subPath = re.escape(subPath)

                    # Download and unzip the selected subtitles (with progressbar)
                    subPath = subPath.replace("\\", "")
                    process_subtitlesDownload = downloadQt(subURL,subPath)
                    
                    # If an error occurs, say so
                    if process_subtitlesDownload != 0:
                        superPrint("error", "Subtitling error!", "An error occurred while downloading or writing <b>" + subtitlesList['data'][subIndex]['LanguageName'] + "</b> subtitles for <b>" + videoTitle + "</b>.")
                        osd_server.LogOut(session['token'])
                        sys.exit(2)

            # Print a message if no subtitles have been found, for any of the languages
            if searchLanguageResult == 0:
                superPrint("info", "No subtitles found for: " + videoFileName, '<b>No subtitles found</b> for this video:\n<i>' + videoFileName + '</i>')
                ExitCode = 1
            else:
                ExitCode = 0

except (OSError, IOError, RuntimeError, TypeError, NameError, KeyError):

    # Do not warn about remote disconnection # bug/feature of python 3.5?
    if "http.client.RemoteDisconnected" in str(sys.exc_info()[0]):
        sys.exit(ExitCode)

    # An unknown error occur, let's apologize before exiting
    superPrint("error", "Unexpected error!", "OpenSubtitlesDownloadQt encountered an <b>unknown error</b>, sorry about that...\n\n" + \
               "Error: <b>" + str(sys.exc_info()[0]).replace('<', '[').replace('>', ']') + "</b>\n\n" + \
               "Just to be safe, please check:\n- www.opensubtitles.org availability\n- Your downloads limit (200 subtitles per 24h)\n- Your Internet connection status\n- That are using the latest version of this software ;-)")

except Exception:

    # Catch unhandled exceptions but do not spawn an error window
    superPrint("error:", "Unknown error!", str(sys.exc_info()[0]))

# Disconnect from opensubtitles.org server, then exit
if session['token']: osd_server.LogOut(session['token'])
sys.exit(ExitCode)
