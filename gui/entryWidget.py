# import PyQt5
import sys,os
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
import subprocess
import gui.specialWidget as oQt
from gui.editentry import EditEntry
from io import StringIO
from gui.pdfButton import pdfButton

import custom

import logging

logger = logging.getLogger(__name__)

pdfFileTypes = ('.pdf','.djvu')

class EntryWidget(QtWidgets.QFrame):
    #replaceChars = lambda self, myStr: str.join('',[self.charmap.get(c,c) for c in str(myStr)])

    CONST_ASCIISTAR = 9734      # A nice ascii star 
    # default font sizes
    defaultTitleFontSize = 20
    defaultMinorTitleFontSize = 18
    defaultButtonFontSize = 10
    defaultTextFontSize = 12
    defaultPrintedTitleColor = "rgb(45,45,150)" # Nice chilled dark blue
    
    def __init__(self,data,database,visibleFields,paperBasePath,win_parent):
        # Init the base class
        self.overviewWindow = win_parent
        
        QtWidgets.QGroupBox.__init__(self,win_parent)
        self.dataEntry = data
        self.database = database
        self.paperBasePath = paperBasePath
        self.__readConfigSettings()
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Maximum)

        # Populate the fields in the widget
        self.create_widgets()
        self.setFieldVisibility(visibleFields)
      
        # Set layout
        self.setMinimumWidth(800)
        self.layout().setContentsMargins(3,5,3,0) # left.top.right,bottom
        # Set the style and color of the widget
        self.setStyleSheet('QFrame {background-color: rgb(236,232,228);}')
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)


        
    def __readConfigSettings(self):
        # get font size and text colors from the config file, if defined
        self.titleFontSize = int(custom.config.get("font","mainTitle",fallback = self.defaultTitleFontSize))
        self.minorTitleFontSize = int(custom.config.get("font","minorTitle",fallback = self.defaultMinorTitleFontSize))
        self.textFontSize = int(custom.config.get("font","text",fallback = self.defaultTextFontSize))
        self.buttonFontSize = int(custom.config.get("font","button",fallback = self.defaultButtonFontSize))
        self.printedTitleColor = str(custom.config.get("color","printedTitle",fallback = self.defaultPrintedTitleColor))
        
    def setFieldVisibility(self,visibleFields):
        fields = {'Authors','Keywords','Abstract','Summary','BibTex'}
        for field in fields:
            if field not in visibleFields:
                self.textfields[field].hide()
            else:
                self.textfields[field].show()

        if 'Buttons' not in visibleFields:
            self.buttons.hide()
        else:
            self.buttons.show()
     
        
    def create_widgets(self):
        # make all possible widgets
        #title = QtWidgets.QRadioButton(self.dataEntry.title)
        if self.dataEntry.favorite == 1: # Put a star in front of favorite titles
            title = QtWidgets.QLabel(("%s %c " %(self.dataEntry.title, self.CONST_ASCIISTAR)),self)
        else:
            title = QtWidgets.QLabel(self.dataEntry.title,self)
            
        title.setFont(QtGui.QFont("Arial",self.titleFontSize,QtGui.QFont.Bold))
        if (self.dataEntry.printed==1):
            title.setStyleSheet("QLabel {color: "+self.printedTitleColor +";}")
        title.setWordWrap(True)

        id = oQt.CopyToClipboardLabelWidget(self.dataEntry.entryId,self.dataEntry.entryId,self)
        id.setFont(QtGui.QFont("Arial",self.minorTitleFontSize))
        id.clicked.connect(self.__copyToClipboard)

        editButton = QtWidgets.QPushButton("Edit",self)
        editButton.clicked.connect(self.__editEntry)
        editButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        deleteButton = QtWidgets.QPushButton("Delete",self)
        deleteButton.clicked.connect(self.__deleteEntry)
        deleteButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)

        self.authorField = self.__makeLabelField(None,self.dataEntry.author)
        self.keywordField = self.__makeLabelField(None,str.join(', ',self.dataEntry.keywords))
        self.abstractField =self.__makeLabelField("Abstract:",self.dataEntry.abstract)
        self.summaryField = self.__makeLabelField("Summary:",self.dataEntry.summary)
        self.bibField = self.__makeCopyClipboardLabelField("BibTex:",self.dataEntry.bibtex)
        
        self.textfields = { 'Keywords': self.keywordField,
                            'Authors': self.authorField,
                            'Abstract': self.abstractField,
                            'Summary': self.summaryField,
                            'BibTex': self.bibField}
            
        pdfFileButton = pdfButton("Open Pdf",self)
        pdfFileButton.setFont(QtGui.QFont("Arial",self.buttonFontSize))
        pdfFilePath = os.path.join(self.paperBasePath,self.dataEntry.pdfFile)
        if self.dataEntry.pdfFile.rstrip().endswith(pdfFileTypes) and os.path.isfile(pdfFilePath):
            pdfFileButton.setPdfFilePath(pdfFilePath)
        else:
            pdfFileButton.setEnabled(False)
            if not self.dataEntry.pdfFile.rstrip().endswith(pdfFileTypes):
                pdfFileButton.setToolTip('PDF file not specified')
            else:
                pdfFileButton.setToolTip('Pdf file not found')
            
            
        deleteButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)


        # do the layout
        layout=QtWidgets.QVBoxLayout()
        
        titleLayout = QtWidgets.QHBoxLayout()
        titleLayout.addWidget(title,1)
        titleLayout.addWidget(id)
        titleLayout.addSpacing(25)
        titleLayout.addWidget(editButton)
        titleLayout.addWidget(deleteButton)
        
        layout.addLayout(titleLayout)
        layout.addWidget(self.textfields["Keywords"],1)
        layout.addWidget(self.textfields["Authors"],1)
        layout.addWidget(self.textfields["Abstract"],1)
        layout.addWidget(self.textfields["Summary"],1)
        layout.addWidget(self.textfields["BibTex"],1)


        # add buttons
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(pdfFileButton)

        for key in self.textfields:
            buttonLayout.addWidget(self.__makeShowButton(key))

        buttonLayout.addStretch(1)
        self.buttons = QtWidgets.QWidget(self)
        self.buttons.setLayout(buttonLayout)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

        # connect the functions
        pdfFileButton.clicked.connect(self.__openPdf)

    # change this away from html style
    def __makeLabelField(self,title,text):
        if(title == None):
            field = QtWidgets.QLabel(text,self)
            field.setFont(QtGui.QFont("Arial",self.textFontSize))
            field.setWordWrap(True)
        else:
            temp = " <span style=\"font-size:" + str(self.textFontSize) + "pt;font-weight:600\"> " + title + "</span>"
            temp = temp + "<span style=\"font-size:" + str(self.textFontSize) + "pt;\">  " + text + " </span> "
            field = QtWidgets.QLabel(temp,self)
            field.setFont(QtGui.QFont("Arial",self.buttonFontSize))
            field.setWordWrap(True)
        return field


    
    def replaceCharsToHTML(self,text):
        charmap = {'\n ' : '<br>&#160;&#160;',
                   '\n' : '<br>'}
        for key in charmap:
            text = text.replace(key, charmap[key])
        return text

    def replaceCharsToText(self,text):
        charmap = {'<br>': '\n'}
        for key in charmap:
            text = text.replace(key, charmap[key])
        return text

    def __makeCopyClipboardLabelField(self,title,text):
        # Only used for bibtex field at the moment
        temp = "<span style=\"font-size:" + str(self.textFontSize) + "pt;font-weight:600\">" + title + "</span>"
        temp = temp + "<span style=\"font-size:" + str(self.textFontSize) + "pt;\"> " + self.replaceCharsToHTML(text) + "</span>"
        field = oQt.CopyToClipboardLabelWidget(temp,self.replaceCharsToText(text),self)
        field.setFont(QtGui.QFont("Arial",self.buttonFontSize))
        field.setWordWrap(True)
        field.clicked.connect(self.__copyToClipboard)
        return field

    def __makeShowButton(self,text):
        button = QtWidgets.QPushButton(text,self)
        button.setFont(QtGui.QFont("Arial",self.buttonFontSize))
        button.clicked.connect(self.__showItem)
        return button

    # Event processing
    def __printText(self):
        logger.info(self.sender().text())

    def __copyToClipboard(self):
        # pyperclip.copy(self.sender().getClipboardtext())
        clipboard = QtGui.QGuiApplication.clipboard() # Access the system clipboard
        clipboard.setText(self.sender().getClipboardtext(),QtGui.QClipboard.Clipboard)

    def __openPdf(self):
        path = os.path.join(self.paperBasePath,self.dataEntry.pdfFile)
        subprocess.call("okular \"" + path + "\" >> /dev/null 2>&1 &",shell=True)

    # here is an error somehow the pushbutton adds & to the text Fix this
    def __showItem(self):
        key = self.sender().text().replace("&","")
        logger.warning(key)
        if(self.textfields[key].isVisible()):
            self.textfields[key].hide()
        else:
            self.textfields[key].show()
        
    def __editEntry(self):
        self.overviewWindow.editEntryById(self.dataEntry.entryId)
        
    def __deleteEntry(self):
        logger.error("Delete Entry: TODO")

    def updated(self):
        # fix update here
        self.window().updated()

