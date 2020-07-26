from ..misc import *
from PyQt5.QtCore import pyqtSlot,  pyqtSignal
from ..gui.addentry import AddEntry

from .. import custom

class EditEntry(AddEntry):
    
    def __init__(self,db,entry,parent=None,mainWindow=None):
        super(EditEntry,self).__init__(db,entry,parent,mainWindow)
        
        
        self.handler.entry = entry
        self.handler.originalID = entry.entryId # This has to be preserved, since the mainWindow
        self.initFields()

        self.handler.entryChanged = False

        self.baseWindowTitle = 'Edit entry'
        self.setWindowTitle('%s \"%s\"' %(self.baseWindowTitle, self.handler.entry.entryId))
        # self.IDEdit.setReadOnly(True)
        
    def initFields(self):
        
        self.cbPrinted.setCheckState(int(self.handler.entry.printed * 2))
        self.cbFavorite.setCheckState(int(self.handler.entry.favorite * 2))
        self.paperType.setCurrentIndex(int(self.handler.entry.paperType))
        self.topic.setCurrentIndex(int(self.handler.entry.topic))
        index = self.bibTypeSelector.findText(self.handler.entry.bibType)
        if index == -1:
            self.bibTypeSelector.addItem(self.handler.entry.bibType)
            index = self.bibTypeSelector.findText(self.handler.entry.bibType)
            
        self.bibTypeSelector.setCurrentIndex(index)

        
        self.populateTab2(self.tab2A,self.tab2B,self.handler.entry.bibType)
        self.updateFields(self.handler.entry)
