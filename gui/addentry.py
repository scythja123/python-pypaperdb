
import sys, os
# rootpath = os.path.join(os.path.abspath(os.curdir),'../..')  # Doesn't seem to be used (22-02-2017) delete
# rootpath = sys.path.append(rootpath) # Doesn't seem to be used (22-02-2017) delete
from paperdb.entry import Entry
from PyQt5 import QtGui
from PyQt5 import QtCore 
from PyQt5 import QtWidgets
from misc import *
import re
import logging
log =logging.getLogger(__name__)
import custom

class AddEntryEventHanler():

    entryChanged = False
    originalID = 'NEWENTRY'
    def __init__(self,db,entry=None,parent=None,mainWindow=None):
        if entry == None:
            self.entry = db.getNewEmptyEntry()
        else:
            self.entry = entry
        self.parent = parent
        self.db = db
        self.mainWindow = mainWindow

        

    def editedEvent(self):
        # define the event handling for all the fields in the addEntry window
        self.entryChanged = True

    def bibtexEvent(self,text):
        tmpCursorPos = self.parent.bibtexEdit.textCursor().position();
        tmpCursorDelta = len(text)-len(text.lstrip()) # The leading whitespaces will be removed
        tmpCursorPos = tmpCursorPos - tmpCursorDelta
        self.entry.bibtex = text
        self.parent.updateFields(self.entry)
        self.__moveCursorToPosition(self.parent.bibtexEdit,tmpCursorPos)

    def IDevent(self,text):
        self.entry.entryId = text
        self.parent.updateFields(self.entry)
        self.mainWindow.editIdChanged(self.originalID,self.entry.entryId)
        
    def titleEvent(self,text):

        self.entry.title = text
        self.parent.updateFields(self.entry)

    def pdfFileEvent(self,text):
        self.entry.updatePdfFile(text)
        self.parent.updateFields(self.entry)

    def keywordEvent(self,text):
        self.entry.addKeyword(str(text))
        self.parent.updateFields(self.entry)

    def paperTypeEvent(self,index):
        self.entry.setPaperType(int(index))
        self.editedEvent()

    def topicEvent(self,index):
        self.entry.setTopic(int(index))
        self.editedEvent()

    def cbPrintedEvent(self,state):
        self.entry.setPrinted(int(state/2))
        self.editedEvent()

    def cbFavoriteEvent(self,state):
        self.entry.setFavorite(int(state/2))
        self.editedEvent()

    def bibTypeEvent(self,selectedBibtexIndex):
        # TODO
        log.info("Bibtex Type changed:")
        #(self.parent.bibTypeSelector.itemText(selectedBibtexIndex))
        
        self.entry.bibType = self.parent.bibTypeSelector.itemText(selectedBibtexIndex)

        self.parent.lostBibtexFields = self.parent.populateTab2(self.parent.tab2A,self.parent.tab2B,self.entry.bibType)
        if self.parent.lostBibtexFields:
            self.parent.looseBibtex(','.join(self.parent.lostBibtexFields))
        self.parent.updateFields(self.entry)


    def eventSave(self,IDtext): # Save all fields to Entry, then store

        self.parent._saveActiveWidget()

        idtext = str(IDtext)
        if len(self.entry.entryId) is 0:
             self.parent.IDempty("No ID provided")
        elif len(self.entry.title) is 0:
            self.parent.IDempty("No Title provided")
        elif len(self.entry.keywords) is 0:
            self.parent.IDempty("At least one keyword needed")
        # elif len(self.entry.summary) is 0:
        #     self.parent.IDempty("Emptry summary provided")
        else:
            if not idtext == self.entry.iddb:
                if  self.db.existsid(idtext): #CHANGED: searchid(idtext) is not None:
                    # Make dialog with warning
                    self.parent.IDexists(idtext)
                    return 0
                else:
                    self.__saveEntry()
                    return 1
            else:
                self.__saveEntry()
                return 1
           
            
    def __saveEntry(self):
        self.parent.statusbar.showMessage('Entry saved')
        self.db.save(self.entry)        
        self.entryChanged = False
        self.parent.setWindowTitle('%s \"%s\"' %(self.parent.baseWindowTitle,self.entry.entryId))
        
    # FIX ME: remove new lines ???
    def abstractValueChangedEvent(self,text): # To remove newline characters from pasted abstract
        
        if QtWidgets.QApplication.clipboard().text() == text:
            self.parent.abstractEdit.setText(self.db.removeNewline(str(text)))
            self.abstractEvent()

    # bibtex fields
    def fieldEvent(self,name,text):
        self.entry.setBibinfo(name,text)
        self.parent.updateFields(self.entry)

    def authorEvent(self,text):
        self.entry.author = text
        self.parent.updateFields(self.entry)
        
    def journalEvent(self,text):
        self.entry.journal = text
        self.parent.updateFields(self.entry)

    def yearEvent(self,text):
        self.entry.year = text
        self.parent.updateFields(self.entry)

    def link2pdfEvent(self,text):
        self.entry.link2pdf = text
        self.parent.updateFields(self.entry)
 
    # FIX ME: remove new lines ???
    def abstractEvent(self,text):
        tmpCursorPos = self.parent.abstractEdit.textCursor().position();
        tmpCursorDelta = len(text)-len(text.lstrip()) # The leading whitespaces will be removed
        tmpCursorPos = tmpCursorPos - tmpCursorDelta
        self.entry.updateAbstract(text)
        self.parent.updateFields(self.entry)
        self.__moveCursorToPosition(self.parent.abstractEdit,tmpCursorPos)

    def summaryEvent(self,text):
        tmpCursorPos = self.parent.summaryEdit.textCursor().position();
        self.entry.updateSummary(text)
        self.parent.updateFields(self.entry)
        self.__moveCursorToPosition(self.parent.summaryEdit,tmpCursorPos)
        
    def citingEvent(self,text):
        self.entry.addCiting(text)
        self.parent.updateFields(self.entry)

    def reject(self):
        # Called when the dialog is closed
        if self.checkSaved() is True:
            QtWidgets.QDialog.reject(self)
   
    def eventDone(self):
        self.parent.close()  # Calls close event

    def __moveCursorToPosition(self,widget,position):
        for i in range(0,position):
            widget.moveCursor(QtGui.QTextCursor.Right,QtGui.QTextCursor.MoveAnchor)
        
    def __del__(self):
        log.info("delete eventhandler")


# Add Entry window to insert a new bibliography entry into the database
class AddEntry(QtWidgets.QDialog):
    
    entryChanged = False

    def __init__(self,db,entry=None, parent=None,mainWindow=None):
        self.mainWindow = mainWindow
        QtWidgets.QDialog.__init__(self,parent)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)
        self.handler = AddEntryEventHanler(db,entry,self,mainWindow)

        if entry == None:
            self.entry = db.getNewEmptyEntry()
        else:
            self.entry = entry

        self.db = db

        user = custom.config.get('user','user',)
        self.kwd = db.getKeywords(user)
        self.requiredFields = list([])
        self.optionalFields = list([])       
        self.initUI()

     
    def keyPressEvent(self,ev):
        if (ev.key() == QtCore.Qt.Key_Enter) or (ev.key() == QtCore.Qt.Key_Return):
            return              # We want to ignore Enter key presses
        elif ev.key() == QtCore.Qt.Key_Escape: 
            self.handler.eventDone() # Call the close event
        else:
            super().keyPressEvent(ev) # Pass it on to the parent event handler

    # function that builds the gui
    def initUI(self):        
       
        self.tabs = QtWidgets.QTabWidget()
        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        self.tab2A = QtWidgets.QFormLayout()
        self.tab2B = QtWidgets.QFormLayout()

        self.lostBibtexFields = None
        # define all elements that will appear.
        menubar = QtWidgets.QMenuBar()
        self.statusbar = QtWidgets.QStatusBar()
        
        kwdCompleter = CustomCompleter(self.kwd)
        kwdCompleter.setWrapAround(False)
        kwdCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        kwdCompleter.setCompletionMode(0)

        self.cbPrinted = QtWidgets.QCheckBox('&Printed',self)
        self.cbPrinted.stateChanged.connect(self.handler.cbPrintedEvent)

        self.cbFavorite = QtWidgets.QCheckBox('&Favorite',self)
        self.cbFavorite.stateChanged.connect(self.handler.cbFavoriteEvent)
        
        self.paperType = QtWidgets.QComboBox(self)

        entryTypes = self.db.getAllEntryTypes()

        if entryTypes:          # Only if entrytypes are defined in database
            for entryType in entryTypes:
                self.paperType.addItem(entryType)
            
        self.paperType.currentIndexChanged.connect(self.handler.paperTypeEvent)

        self.topic = QtWidgets.QComboBox(self)

        topics = self.db.getAllTopics()

        if topics:              # Only if topics are defined in database
            for topic in topics:
                self.topic.addItem(topic)
            
        self.topic.currentIndexChanged.connect(self.handler.topicEvent)
        btn2 = QtWidgets.QPushButton('&Done',self)
        btn2.setShortcut('Ctrl+Q')
        btn2.resize(btn2.sizeHint())
        btn2.clicked.connect(self.handler.eventDone) 
        

        btnSave = QtWidgets.QPushButton('&Save',self)
        btnSave.setShortcut('Ctrl+S')
        btnSave.resize(btnSave.sizeHint())
        btnSave.clicked.connect(lambda: self.handler.eventSave(self.IDEdit.text()))

        # btnBibtexInsert = QtWidgets.QPushButton('Insert', self)
        # btnBibtexInsert.clicked.connect(lambda: self.handler.eventAddBibtex(self.boxBibtexSelector.currentText()))

        # self.boxBibtexSelector = QtWidgets.QComboBox(self)
        # for type in self.config.options('bibTexSceletons'):
        #     self.boxBibtexSelector.addItem(type)
        
        # select the bibtex Type:
        self.bibTypeSelector = QtWidgets.QComboBox(self)
        self.knownBibTypes = custom.config.get('bibtexTypes','bibtexTypes')
        self.knownBibTypes = str.split(self.knownBibTypes,',')
        #print(self.knownBibTypes)
        for bibtype in self.knownBibTypes:
            self.bibTypeSelector.addItem(bibtype)

        self.bibTypeSelector.currentIndexChanged.connect(self.handler.bibTypeEvent)
        
        # Tab1 : general fields
        self.IDEdit = QtWidgets.QLineEdit()
        self.titleEdit = QtWidgets.QLineEdit()
        self.pdfFileEdit = QtWidgets.QLineEdit()
        self.keywordEdit = QtWidgets.QLineEdit()
        self.keywordEdit.setCompleter(kwdCompleter)
        self.summaryEdit = EnhancedTextEdit()
        self.abstractEdit = EnhancedTextEdit()
        self.bibtexEdit = EnhancedTextEdit()
       

        ### Connect the signals
        self.IDEdit.editingFinished.connect(lambda: self.handler.IDevent(self.IDEdit.text()))
        self.titleEdit.editingFinished.connect(lambda: self.handler.titleEvent(self.titleEdit.text()))
        self.pdfFileEdit.editingFinished.connect(lambda: self.handler.pdfFileEvent(self.pdfFileEdit.text()))
        self.keywordEdit.editingFinished.connect(lambda: self.handler.keywordEvent(self.keywordEdit.text()))
        self.abstractEdit.editingFinished.connect(lambda: self.handler.abstractEvent(self.abstractEdit.toPlainText())) #calls event to remove newline chars from pasted abstract
        self.summaryEdit.editingFinished.connect(lambda: self.handler.summaryEvent(self.summaryEdit.toPlainText()))
        self.bibtexEdit.editingFinished.connect(lambda: self.handler.bibtexEvent(self.bibtexEdit.toPlainText()))
        


        self.IDEdit.textChanged.connect(self.handler.editedEvent)
        self.titleEdit.textChanged.connect(self.handler.editedEvent)
        self.pdfFileEdit.textChanged.connect(self.handler.editedEvent)
        self.keywordEdit.textChanged.connect(self.handler.editedEvent)
        self.abstractEdit.textChanged.connect(self.handler.editedEvent)
        self.summaryEdit.textChanged.connect(self.handler.editedEvent)
        self.bibtexEdit.textChanged.connect(self.handler.editedEvent)
        

        ### Layout
        ## tab 1
        labels = ['Topi&c','&Entry type', '&ID', '&Title', 'PDF &file', '&Keywords', 'Su&mmary', '&Abstract', '&Bibtex']
        
        
        fields = (self.topic,self.paperType, self.IDEdit, self.titleEdit, self.pdfFileEdit, self.keywordEdit, 
                  self.summaryEdit, self.abstractEdit, self.bibtexEdit)
        
        # insert the fields into the layout
        grid1 = QtWidgets.QGridLayout()
        grid1.setSpacing(10)
        
        pos = 0
        posy = 0
        for index, label in enumerate(labels):
            lbl = QtWidgets.QLabel(label)
            lbl.setBuddy(fields[index])
            grid1.addWidget(lbl ,pos ,posy)
            pos+=1
            
        pos = 0
        posy = 1
        for field in fields:
            grid1.addWidget(field, pos, posy)
            pos+=1

        grid1.addWidget(self.bibTypeSelector,pos,1)
        # grid1.addWidget(btnBibtexInsert,pos,0)
        
        pos += 1
        grid1.addWidget(self.cbPrinted,pos,0)
        grid1.addWidget(self.cbFavorite,pos,1)
        

        # make tab 2:
        self.populateTab2(self.tab2A,self.tab2B,self.entry.bibType)
        grid2 = QtWidgets.QVBoxLayout()
        grid2.addWidget(QtWidgets.QLabel("Required"))
        grid2.addLayout(self.tab2A)
        grid2.addWidget(QtWidgets.QLabel("Optional"))
        grid2.addLayout(self.tab2B)
        ## Buttons
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(btn2)
        hbox.addWidget(btnSave)
                
        ## Set main layout
        self.tab1.setLayout(grid1)
        self.tab2.setLayout(grid2)

        self.resize(800,600)
        self.baseWindowTitle = 'Add new entry'
        self.setWindowTitle(self.baseWindowTitle)
        
        self.tabs.addTab(self.tab1,"&General")
        self.tabs.addTab(self.tab2,"E&xtra")
        
        mainLayout = QtWidgets.QVBoxLayout()
        # mainLayout.addStretch(1)
        mainLayout.addWidget(self.tabs)
        mainLayout.addLayout(hbox)
        self.setLayout(mainLayout)

        self.show()       


    def IDexists(self,idtext):
        QtWidgets.QMessageBox.information(self,"Warning - entry not saved", "ID %s already exists in database.\nPlease use another ID" %idtext)
    
    def IDempty(self,missingField):
        QtWidgets.QMessageBox.information(self,"Warning - entry not saved", "Entry not saved: %s." %missingField)
        

    def looseBibtex(self,missingField):
        QtWidgets.QMessageBox.information(self,"Warning - some bibtex fields are no longer allowed", "BibTex fields are no longer allowed:\n %s \n Please use another bibType or accept the loss." %missingField)

    def notADefinedBibtex(self,bibType):
        QtWidgets.QMessageBox.information(self,"Warning - The bibtex type is not known:\n %s \n It will be treated as a misc entry." %bibType)

    def closeEvent(self,event):
        
        if self.checkSaved() is True:
            self.mainWindow.editEnded(self.handler.originalID) # Notify main window that we close
            self.mainWindow.updated()
            event.accept()
        else:
            event.ignore()

    def _saveActiveWidget(self):
        fw = QtWidgets.QApplication.focusWidget()
        
        if isinstance(fw,QtWidgets.QLineEdit):
            fw.editingFinished.emit()
        elif isinstance(fw,EnhancedTextEdit):
            fw.editingFinished.emit()

    def checkSaved(self):
        if self.handler.entryChanged is True:
            # dialog unsaved entry (cancel, exit, save)
            reply = QtWidgets.QMessageBox.question(self,'Unsaved Progress','Unsaved changes are made in the entry', QtWidgets.QMessageBox.Save|QtWidgets.QMessageBox.Close| QtWidgets.QMessageBox.Cancel)

            if reply == QtWidgets.QMessageBox.Save:
                saved = self.handler.eventSave(self.IDEdit.text())
                if saved == 1:
                    return True
            elif reply == QtWidgets.QMessageBox.Close:
                return True
            else:
                return False
        else:
            return True


    def updateFields(self,entry):

        self.IDEdit.setText(entry.entryId)
        self.titleEdit.setText(entry.title)
        self.bibtexEdit.setText(entry.bibtex)
        self.summaryEdit.setText(entry.summary)
        self.abstractEdit.setText(entry.abstract)
        self.pdfFileEdit.setText(entry.pdfFile)
        #self.link2pdfEdit.setText(entry.link2pdf)
        #self.citingEdit.setText(entry.citing)
        #self.authorEdit.setText(entry.author)
        #self.yearEdit.setText(entry.year)
        #self.journalEdit.setText(entry.journal)
        log.debug("update Fields")
        for field in self.requiredFields:
            log.debug("getBibinfo: " + self.entry.getBibinfo(field[0]))
            field[1].setText(entry.getBibinfo(field[0]))
        
        for field in self.optionalFields:
            field[1].setText(entry.getBibinfo(field[0]))

            kwdstr = ""
        for kwd in self.handler.entry.keywords:
            kwdstr = kwdstr + str(kwd) + ", "
        kwdstr = kwdstr[0:-2]

        self.keywordEdit.setText(kwdstr)

    def populateTab2(self,layout,optLayout,bibType):
        # Tab2: required Bibtex fields
        # TODO: add check whether section actually exists

        # MAKE required fields
        if bibType not in self.knownBibTypes:
            #self.notADefinedBibtex(bibType)
            bibType = 'misc'

            
        fields = custom.config.get(bibType,'requiredFields')
        fields = str.split(fields,', ')
        optfields = custom.config.get(bibType,'optionalFields')
        optfields = str.split(optfields,', ')
                
        log.info('Required Fields:\n\t' + ', '.join(fields))

        newFields = fields
        fieldsNoLongerAllowed = list([])
        fieldsToDeleteFromRequired = list([])

        for existingField in self.requiredFields:
            log.debug('check: ' + existingField[0])

            if existingField[0] in fields:
                log.debug('keep')
                newFields.remove(existingField[0])                
            else:
                log.debug('remove')
                if existingField[0] not in optfields:
                    fieldsNoLongerAllowed.append(existingField[0])

                label = layout.labelForField(existingField[1])
                if label is not None:
                    label.deleteLater()
                existingField[1].deleteLater()
                fieldsToDeleteFromRequired.append(existingField)
                #self.requiredFields.add((name,self.__makeTextField(field)))

        log.debug("Remove fields from required list")
        for deletingFields in fieldsToDeleteFromRequired:
            self.requiredFields.remove(deletingFields)
        
        log.debug('Fields to create newly:\n\t' + ', '.join(newFields))
        if newFields:
            for field in newFields:
                self.requiredFields.append((field,self.__makeTextField(field)))
                layout.addRow(field,self.requiredFields[-1:][0][1])


        # MAKE optional fields
        newFields = optfields
        
        fieldsToDeleteFromOptional = list([])
        
        for existingField in self.optionalFields:
            log.debug('check: ' + existingField[0])
            
            if existingField[0] in optfields:
                log.debug('keep')
                newFields.remove(existingField[0])
            else:
                log.debug('remove')

                if existingField[0] not in fields:
                    fieldsNoLongerAllowed.append(existingField[0])

                label = optLayout.labelForField(existingField[1])
                if label is not None:
                    label.deleteLater()
                existingField[1].deleteLater()
                fieldsToDeleteFromOptional.append(existingField)
                #self.requiredFields.add((name,self.__makeTextField(field)))

        log.debug("Remove fields from required list")
        for deletingFields in fieldsToDeleteFromOptional:
            self.optionalFields.remove(deletingFields)
        
        log.debug('Fields to create newly:\n\t' + ', '.join(newFields))
        
        if newFields:
            for field in newFields:
                self.optionalFields.append((field,self.__makeTextField(field)))
                optLayout.addRow(field,self.optionalFields[-1:][0][1])

        
        return fieldsNoLongerAllowed

    
    def __makeTextField(self,name):
        # self.journalEdit = QtWidgets.QLineEdit()
        field = QtWidgets.QLineEdit()
        #field.setText(self.entry.getBibinfo(name))

        # self.journalEdit.editingFinished.connect(lambda: self.handler.journalEvent(self.journalEdit.text()))
        field.editingFinished.connect(lambda: self.handler.fieldEvent(name,field.text()))

        # self.journalEdit.textChanged.connect(self.handler.editedEvent)
        field.textChanged.connect(self.handler.editedEvent)
        
        return field
