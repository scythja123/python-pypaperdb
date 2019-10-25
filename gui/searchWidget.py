import sys
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
import re
import time
import logging
log =logging.getLogger(__name__)

if __name__ == "__main__":
    # Someone launches this class directly
    print("please run application to start Paperdatabase")

class SearchWidget(QtWidgets.QScrollArea):

    searchList =[]
    
    def __init__(self,topicList,entryTypeList,win_parent=None):
        # Init the base class
        QtWidgets.QScrollArea.__init__(self,win_parent)

        self.topicList = topicList
        self.entryTypeList = entryTypeList

        self.layout = QtWidgets.QVBoxLayout()
        self.__addNewSearchLine()
       
        areaWidget = QtWidgets.QWidget()
        areaWidget.setLayout(self.layout)
        #areaWidget.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
        self.setWidget(areaWidget)
        self.setWidgetResizable(True)

        # The below activates the first searchbar when Ctrl+F is pressed
        self.searchAct = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+F'),self)
        self.searchAct.setContext(QtCore.Qt.WindowShortcut)
        self.searchAct.activated.connect(self.searchList[0].keywordField.setFocus)

        # This timer is used when focus is lost in the search field. It makes sure that the focusEvent for the new widget in focus is handled first before updating the entrylist. This should prevent segfaults when clicking on the entryfields after entering a search term
        self.timeoutTimer = QtCore.QTimer()
        self.timeoutTimer.setInterval(1) # wait for 1 ms
        self.timeoutTimer.setSingleShot(True)

   
        
    def __addNewSearchLine(self):
        log.info('newsearchline - number of searches ' + str(len(self.searchList)))
        numberOfLines = len(self.searchList)
        self.searchList.append(SearchCommandWidget(self.topicList,self.entryTypeList))
        if numberOfLines > 0:
            self.searchList[numberOfLines-1].keywordField.textEdited.disconnect(self.__addNewSearchLine)
            
        #has to be improved to happen if some text is entered
        self.searchList[numberOfLines].keywordField.textEdited.connect(self.__addNewSearchLine)
        self.searchList[numberOfLines].keywordField.editingFinished.connect(self.__modifiedKeywords)
        # self.searchList[numberOfLines].keywordField.focusOutEvent.connect(self.__focusLost)
        
        # # Not yet implemented!!
        # self.searchList[numberOfLines].removeButton.clicked.connect(self.__remove)

        self.searchList[numberOfLines].locationField.activated.connect(self.__locationChanged)
        self.searchList[numberOfLines].typeField.activated.connect(self.__typeChanged)
        self.searchList[numberOfLines].topicField.activated.connect(self.__topicChanged)
        self.searchList[numberOfLines].removeButton.clicked.connect(self.__removeSearchLine)
        
        self.layout.insertWidget(numberOfLines,self.searchList[numberOfLines])
        self.layout.addStretch(1)
        
    def __removeSearchLineByIndex(self,index=0):
        removed_search = self.searchList.pop(index)
        numberOfLines = len(self.searchList)
        # if the last search field should be removed we have to disconnect and reconnect the action to generate new search fields
        if index == numberOfLines:
            removed_search.keywordField.textEdited.disconnect()
            if numberOfLines > 0:
                #has to be improved to happen if some text is entered
                self.searchList[numberOfLines-1].keywordField.textEdited.connect(self.__addNewSearchLine)
            else:
                self.__addNewSearchLine()
                
        removed_search.keywordField.editingFinished.disconnect()
        # # Not yet implemented!!
        # self.searchList[numberOfLines].removeButton.clicked.disconnect(self.__remove)
        removed_search.locationField.activated.disconnect()
        removed_search.typeField.activated.disconnect()
        removed_search.topicField.activated.disconnect()
        removed_search.removeButton.clicked.disconnect()
        self.layout.removeWidget(removed_search)

    def change_topic_entrytype(self, new_topicList, new_entry_type_list):
        self.topicList = new_topicList
        self.entryTypeList = new_entry_type_list
        for i in range(len(self.searchList)):
            self.__removeSearchLineByIndex()
        self.parent().parent().updated()

    def returnSearchList(self):
        keywordList = []
        if len(self.searchList)==1:
            keywordList.append(self.searchList[0].getSelection())
        else:
            for line in self.searchList[:-1]:
                keywordList.append(line.getSelection())
        return keywordList

    def __modifiedKeywords(self):
        log.info("keyword modified: "+ self.sender().text())

        if self.sender().isModified():
            if not self.sender().hasFocus():
                # If the modified signal is triggered due to a focus loss, we have to make sure that there are no untriggered events from the entryfield. Therefore we pause this event for a very short time, while the others can be handled            
                self.timeoutTimer.timeout.connect(self.parent().parent().updated)
                self.timeoutTimer.start()
                self.sender().setModified(False)
            else:
                # If no focus loss, there is no reason to wait
                self.parent().parent().updated()
                self.sender().setModified(False)

    def __locationChanged(self):
        log.info("location changed: " + self.sender().currentText())
        self.parent().parent().updated()

    def __typeChanged(self):
        log.info("type changed: " + self.sender().currentText())
        self.parent().parent().updated()

    def __topicChanged(self):
        log.info("topic changed: " + self.sender().currentText())
        self.parent().parent().updated()
        
    def __removeSearchLine(self):
        keywordLine = self.sender().parent()
        if keywordLine in self.searchList:
             self.searchList.remove(keywordLine)
             self.layout.removeWidget(keywordLine)
             self.parent().parent().updated()

class SearchCommandWidget(QtWidgets.QFrame):

    searchLocations = ["any","title","keyword","author","summary","abstract","year","journal","id"] # todo make them in config file
    defaultLocationField = "any"
    
    def __init__(self,topicList,entryTypeList,win_parent=None):
        QtWidgets.QGroupBox.__init__(self,win_parent)
        
        self.entryTypes = entryTypeList
        self.topics = topicList # set topiclist
        
        log.info("defaultLocationField: " + self.defaultLocationField)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)

        self.typeField = QtWidgets.QComboBox()
        if self.entryTypes: # Only add entrytypes if they exist in the database
            self.typeField.insertItems(0,sorted(self.entryTypes))
        self.typeField.addItem("any")
        self.typeField.setCurrentIndex(self.typeField.findText("any"))

        self.topicField = QtWidgets.QComboBox()
        if self.topics:         # Only add topics if they exist in the database
            self.topicField.insertItems(0,sorted(self.topics))
        self.topicField.addItem("any")
        self.topicField.setCurrentIndex(self.topicField.findText("any"))
        
        self.keywordField = QtWidgets.QLineEdit()
        # self.keywordField.focusOutEvent(QtCore.Qt.NoFocus)
        self.keywordField.setPlaceholderText("Please insert search words, comma separated")
        self.keywordField.setText(' ')
        self.locationField = QtWidgets.QComboBox()
        self.locationField.insertItems(0,sorted(self.searchLocations)) # add the list of search locations alphabetically
        self.removeButton = QtWidgets.QPushButton("-")
        self.locationField.setCurrentIndex(self.locationField.findText(self.defaultLocationField))  # Set default search location

        layout=QtWidgets.QVBoxLayout()
        # layout.setContentsMargins(0,0,0,0)
        
        layoutTemp = QtWidgets.QHBoxLayout()
        layoutTemp.addWidget(self.typeField)
        layoutTemp.addWidget(self.topicField)
        layout.addLayout(layoutTemp)
        
        layoutTemp = QtWidgets.QHBoxLayout()
        layoutTemp.addWidget(self.keywordField)
        layoutTemp.addWidget(self.locationField)
        layoutTemp.addWidget(self.removeButton)
        layout.addLayout(layoutTemp)
        
        self.setLayout(layout)
        self.setContentsMargins(1,1,1,1)
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
         

    def getSelection(self):
        if self.entryTypes:     # Only if entrytypes are given in the database
            try:
                papertype=self.entryTypes.index(self.typeField.currentText())
            except ValueError:
                papertype = None
        else:
            papertype = None
            
        if self.topics:         # Only if topics are given in the database
            try:
                topic=self.topics.index(self.topicField.currentText())
            except ValueError:
                topic = None
        else:
            topic = None

        log.info('selection: ' + self.keywordField.text())
        return (self.keywordField.text(),self.locationField.currentText(),papertype,topic)

    def __printTest(self):
        print("test")
        
