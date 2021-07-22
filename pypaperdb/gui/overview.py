#! /usr/bin/env python
import sys,os, collections
from operator import attrgetter # for the sorting algorithm
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from ..gui.addentry import AddEntry
from ..gui.editentry import EditEntry
from ..gui.entryWidget import EntryWidget
from ..gui.searchWidget import SearchWidget
import time
import logging


log = logging.getLogger(__name__)

from .. import  custom

class OverviewWindow(QtWidgets.QMainWindow):

    visibleFields = set()    # Will be filled in the initialization.
    entriesEditedHandles = dict()  # This dict contrains entries and window handles that are being edited See description under editEntryById
    defaultSpacing = 5             # default spacing between search widgets and entries
    
    def __init__(self,database,win_parent=None):
        QtWidgets.QMainWindow.__init__(self,win_parent)
        
        # pointer to database
        self.database = database
        log.info(database.basePath)
        path = custom.config.get('user','paperPath')
        self.paperBasePath = os.path.expanduser(path)
        self.paperBasePath = os.path.realpath(self.paperBasePath)
        log.info("Paper Base Path")
        log.info(self.paperBasePath)
        path = custom.config.get('user','bibTexSavePath',fallback = "")
        self.bibTexSavePath = os.path.expanduser(path)
        self.bibTexSavePath = os.path.realpath(self.bibTexSavePath)

        self.topicList =  self.database.getAllTopics()
        self.entryTypeList =  self.database.getAllEntryTypes()

        # Init the base class
        self.setWindowTitle("Paperdatabase Overview")
        try:
            self.__readWindowSettings()
        except:
            # if window settings fail, then just make it default
            self.resize(500,300)
        
        # create the overview pane:
        # Make central widget a scroll area that takes before created  widgets
        central_widget = QEntryArea() #QtWidgets.QScrollArea() #
        #central_widget.setWidget()
        central_widget.setWidgetResizable(True)
        central_widget.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.MinimumExpanding)
        # central_widget.setContentsMargins(0,0,0,0)
        
        self.central_widget = central_widget
        self.setCentralWidget(central_widget)
        
        entries = self.database.getAllEntries()
        self.sortKey = 'entryId'
        entries = sorted(entries,key=attrgetter(self.sortKey), reverse = False)
       
        #Creat menu bar:
        central_menubar = QtWidgets.QMenuBar()        
        entriesMenu = central_menubar.addMenu("&File")
        entriesMenu.addAction(QtWidgets.QAction('&New entry',self,shortcut='Ctrl+N', triggered=self.__newEntry,icon=QtGui.QIcon.fromTheme('document-new')))
        entriesMenu.addAction(QtWidgets.QAction('&Edit entry',self,shortcut='Ctrl+E',triggered=self.__editEntryDialog,icon=QtGui.QIcon.fromTheme('document-edit')))
        entriesMenu.addSeparator()
        entriesMenu.addAction(QtWidgets.QAction('Export &Bibtex',self,shortcut='Ctrl+P',triggered=self.__exportBibtex))
        entriesMenu.addAction(QtWidgets.QAction('Append Bibtex',self,triggered=self.__appendBibtex))
        entriesMenu.addAction(QtWidgets.QAction('Get Bibtex',self,triggered=self.__bibtexfromAux))
        entriesMenu.addSeparator()
        entriesMenu.addAction(QtWidgets.QAction("Cange database",self,triggered=self.__change_database))
        entriesMenu.addSeparator()
        entriesMenu.addAction(QtWidgets.QAction("&Exit",self,shortcut="Ctrl+Q",triggered=self.close,icon=QtGui.QIcon.fromTheme('exit')))

        searchMenu = central_menubar.addMenu("&Search")
        searchMenu.addAction(QtWidgets.QAction('&Show search', self, triggered=self.__showSearchDock))
        searchMenu.addAction(QtWidgets.QAction('&Hide search', self, triggered=self.__hideSearchDock))
        #searchMenu.addAction(QtWidgets.QAction('&Show/Hide search', self, triggered=self.__toggleSearchDock))

        optionMenu = central_menubar.addMenu("&Options")
        optionMenu.addAction(QtWidgets.QAction('&Find missing keys', self, triggered=self.__missing_keys))

        
        viewMenu = central_menubar.addMenu("&View")

        # Submenu for sorting of entries
        sortMenu = viewMenu.addMenu("Sort by")
        sortMenuAG = QtWidgets.QActionGroup(self)
        sortMenuAG.setExclusive(True)
        a = sortMenuAG.addAction(QtWidgets.QAction('ID',self,triggered=lambda: self.__sortEntriesBy('entryId'),checkable=True))
        sortMenu.addAction(a)
        a.setChecked(True)
        a = sortMenuAG.addAction(QtWidgets.QAction('Author',self,triggered=lambda:  self.__sortEntriesBy('author'),checkable=True))
        sortMenu.addAction(a)
        a = sortMenuAG.addAction(QtWidgets.QAction('Title',self,triggered=lambda:  self.__sortEntriesBy('title'),checkable=True))
        sortMenu.addAction(a)
        a = sortMenuAG.addAction(QtWidgets.QAction('Journal',self,triggered=lambda:  self.__sortEntriesBy('journal'),checkable=True))
        sortMenu.addAction(a)
        a = sortMenuAG.addAction(QtWidgets.QAction('Year',self,triggered=lambda:  self.__sortEntriesBy('year'),checkable=True))
        sortMenu.addAction(a)
        a = sortMenuAG.addAction(QtWidgets.QAction('Paper type',self,triggered=lambda:  self.__sortEntriesBy('paperType'),checkable=True))
        sortMenu.addAction(a)
        a = sortMenuAG.addAction(QtWidgets.QAction('Date modified',self,triggered=lambda:  self.__sortEntriesBy('date'),checkable=True))
        sortMenu.addAction(a)
        sortMenu.addSeparator()
        self.entrySortDirection = QtWidgets.QAction('Descending',self,triggered=self.updated,checkable=True)
        sortMenu.addAction(self.entrySortDirection)

        # Submenu for toggling visibility of fields
        # TODO: define in config file which the defaultview is defined.       
        showMenu = viewMenu.addMenu("&Show fields")

        initValues = (True, False, True, False, True, True)


        self.showEntryFields = collections.OrderedDict() # This gives us a set with ordered items
        showMenu.addAction(QtWidgets.QAction('Hide all', self, triggered=self.__hideAll))
        showMenu.addAction(QtWidgets.QAction('Show all', self, triggered=self.__showAll))
        showMenu.addSeparator()
        
        self.showEntryFields['Summary'] = QtWidgets.QAction('Summary', self, triggered=self.__showHideFields,checkable=True)
        self.showEntryFields['Abstract'] = QtWidgets.QAction('Abstract', self, triggered=self.__showHideFields,checkable=True)
        self.showEntryFields['Authors'] = QtWidgets.QAction('Authors', self, triggered=self.__showHideFields,checkable=True)
        self.showEntryFields['BibTex'] = QtWidgets.QAction('BibTex', self, triggered=self.__showHideFields,checkable=True)
        self.showEntryFields['Buttons'] = QtWidgets.QAction('Buttons', self, triggered=self.__showHideFields,checkable=True)
        self.showEntryFields['Keywords'] = QtWidgets.QAction('Keywords', self, triggered=self.__showHideFields,checkable=True)
     
        i=0
        for key,val in self.showEntryFields.items():
            showMenu.addAction(self.showEntryFields[key])
            self.showEntryFields[key].setChecked(initValues[i])
            i +=1

        #showMenu.addAction(QtWidgets.QAction('Hide/Show Keywords', self, triggered=self.__hideBib))

      
        self.setMenuBar(central_menubar)

        # Create search field as and put it in a docket:
        self.searchDock = QtWidgets.QDockWidget("Search",self)
        self.searchDock.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.search = SearchWidget(self.topicList,self.entryTypeList,self)
        self.searchDock.setWidget(self.search)
        self.searchDock.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Preferred)
        self.search.layout.setContentsMargins(0,0,0,0)
        self.search.layout.setSpacing(self.defaultSpacing)
    
        
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea,self.searchDock)

        # Finally we create the entryList
        self.__create_entry_overview(entries)        
        self.__showHideFields()

        # and update list to get all defaults from the search list.
        self.updated()
     
    def __missing_keys(self):
        # todo make option field for recognised words etc.
        log.warning(self.database.get_non_recognised_string_fields('month'))
        

    def __sortEntriesBy(self,sortBy):
        self.sortKey = sortBy      
        self.updated()        
        
    def __showSearchDock(self):
        self.restoreDockWidget(self.searchDock)
    def __hideSearchDock(self):
        self.removeDockWidget(self.searchDock)
    
    def updated(self):
        keywords = self.search.returnSearchList()
        log.info(str(keywords))
        if keywords == []:
            # if no keyword provided we get all entries
            entries = self.database.getAllEntries()
        else:
            # Else we only get the desired entries
            entries = self.database.getEntries(keywords)

        entries = sorted(entries,key=attrgetter(self.sortKey), reverse = self.entrySortDirection.isChecked())
        self.__create_entry_overview(entries)

        
    def __create_entry_overview(self,entriesToShow):
        with Timer() as tmr:
            #Create  entry pane: that contains the database entries:
            entryLayout = QtWidgets.QVBoxLayout()
            # create the enty widgets:
            for entry in entriesToShow:
                entryWid = EntryWidget(entry,self.database,self.visibleFields,self.paperBasePath,self)
                entryWid.hide()     # Hide the widget (will be shown later)
                entryLayout.addWidget(entryWid)

            entryLayout.setContentsMargins(5,5,5,5) # left.top.right,bottom
            entryLayout.setSpacing(self.defaultSpacing)               # spacing in between widgets in the layout
      
            entryPane = QtWidgets.QWidget(self)
            entryPane.setLayout(entryLayout)
            entryPane.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Preferred)


            log.debug('scroll values before update ' + str(self.centralWidget().verticalScrollBar().value()) + ' maximum ' + str(self.centralWidget().verticalScrollBar().maximum()))
            verticalScrollBarOldValue = self.centralWidget().verticalScrollBar().value()
            verticalScrollBarOldMaximum = self.centralWidget().verticalScrollBar().maximum()
            oldEndVisibleEntries = self.centralWidget().endVisibleEntries
        
            self.centralWidget().verticalScrollBar().setValue(0)
            self.centralWidget().setWidget(entryPane)


            # make_entries_visible(self.centralWidget().widget().layout(),0,5)
            make_entries_visible(self.centralWidget().widget().layout(),max(0,oldEndVisibleEntries-25),max(25,oldEndVisibleEntries))

            self.centralWidget().verticalScrollBar().setMaximum(verticalScrollBarOldMaximum)
            self.centralWidget().verticalScrollBar().setValue(verticalScrollBarOldValue)
     
            # print('startentriesvisible ' + str(self.centralWidget().startVisibleEntries))
            # self.centralWidget().startVisibleEntries = max(0,oldEndVisibleEntries - 5)
            log.debug('scroll values after update ' + str(self.centralWidget().verticalScrollBar().value()) + ' maximum ' + str(self.centralWidget().verticalScrollBar().maximum()))
        log.info('time spend in __create_entry_overview(): ' + str(tmr.secs))


    def __hideAll(self):
        # Hide all fields that can be hidden
        for key,val in self.showEntryFields.items():
            val.setChecked(False)
        self.__showHideFields()

    def __showAll(self):
        # Show all fields that can be hidden
        for key,val in self.showEntryFields.items():
            val.setChecked(True)
        self.__showHideFields()
            
    def __showHideFields(self):
        # Hides or shows the fields depending on the boxes that are ticked
        self.visibleFields = set()
        for key,val in self.showEntryFields.items():
            if val.isChecked():
                self.visibleFields.add(key) # This list is used when updating the view settings

        for entry in layout_widgets(self.centralWidget().widget().layout()):
            entry.setFieldVisibility(self.visibleFields) # Update all fields          

    def __newEntry(self):
        if 'NEWENTRY'in self.entriesEditedHandles:
            self.entriesEditedHandles['NEWENTRY'][0].showNormal()
            self.entriesEditedHandles['NEWENTRY'][0].activateWindow()
                
            return
        self.entriesEditedHandles['NEWENTRY'] = [AddEntry(self.database,None,self,self), 'NEWENTRY']
        self.entriesEditedHandles['NEWENTRY'][0].setWindowIcon(self.windowIcon())
            
    def __editEntryDialog(self):
        # TODO: Prevent multiple instances for the same entry
        editID, ok = QtWidgets.QInputDialog.getText(self,"Edit entry","ID:")
        
        if ok and len(editID) > 0:
            entry = self.database.searchEntry(editID)
            if entry is not None:                
                self.editEntryById(editID)
            else:
                QtWidgets.QMessageBox.information(self,"Entry not found", "Entry with ID %s could not be found" %editID)

    def __change_database(self):
        if bool(self.entriesEditedHandles) is True: # check if the set is empty
            # If true, we are still editing entries
            log.warning(str(self.entriesEditedHandles))
            test = QtWidgets.QMessageBox.question(self,"Warning", "Some entries are still being edited. Do you want to continue?")
            if(test == QtWidgets.QMessageBox.No):
                return
        
        # load another database
        fileNameLoad = QtWidgets.QFileDialog.getOpenFileName(self,"Database file to load", self.database.basePath ,"Database files (*.xml);;All files (*.*)")
        if fileNameLoad[0]:   # Only if we actually selected a file
            dbFile = fileNameLoad[0]
            dbFileAbsPath = os.path.expanduser(dbFile)
            dbFileAbsPath = os.path.realpath(dbFileAbsPath)
            log.info(dbFileAbsPath)

            if fileNameLoad[0] is not None:
                if fileNameLoad[0].endswith(".dummydb"):
                    log.info("dummy database")
                    from ..paperdb import dummydb as database
                    self.database = database.Database(dbFileAbsPath)
                elif fileNameLoad[0].endswith(".base"):
                    log.info("base database")
                    from ..paperdb import databaseBase as database
                    self.database = database.Database(dbFileAbsPath)
                elif fileNameLoad[0].endswith(".xml"):
                    log.info("xml database")
                    from ..paperdb import xmldb as database
                    self.database = database.Database(dbFileAbsPath)
                else:
                    log.warning("No database imported.\n")
                    return

                self.updated()
                self.topicList =  self.database.getAllTopics()
                self.entryTypeList =  self.database.getAllEntryTypes()
                self.search.change_topic_entrytype(self.topicList,self.entryTypeList)

            else:
                log.warning("No database imported.\n")

    def editEntryById(self,entryId):
        # Here we first check whether the entry that we want to edit is already being edited. Here we have to check both whether it is the old entryId (in case edit is pressed in the GUI) or the new entryID (in case the edit dialog is used and the ID is proved manually).
        # The edited entries are stored as:
        #   self.entriesEditedHandles[oldEntryId] = [windowHandle,newEntryId]
        # where:
        #   oldEntryId is the ID of the entry when editing started
        #   newEntryId is the most recentrly saved ID of the entry
        #   windowHandle is the handle to the QDialog of that entry
        log.info("Editing entry id " + str(entryId))
        
        if entryId in self.entriesEditedHandles:
            log.warning('Entry ' + str(entryId) + ' is already being edited')
            self.entriesEditedHandles[entryId][0].showNormal()
            self.entriesEditedHandles[entryId][0].activateWindow()

            return
        
        for key,value in self.entriesEditedHandles.items():
            if entryId == value[1]:
                log.warning('Entry ' + str(entryId) + ' is already being edited')
                self.entriesEditedHandles[key][0].showNormal()
                self.entriesEditedHandles[key][0].activateWindow()
                return
                
        
        entry = self.database.searchEntry(entryId)
        if entry is not None:            
            self.entriesEditedHandles[entryId] = [self.__editEntry(entry),entryId] # This dictionary contains window handlesthe entries that currently are being edited
            log.debug("handle to edit entry window: " + str(self.entriesEditedHandles))
          
        else:
            log.warning('Entry %s does not exist in database, are you already editing it?' %str(entryId))
                
    def __editEntry(self,entry):
        editEntry = EditEntry(self.database,entry,parent=None,mainWindow=self)
        editEntry.setWindowIcon(self.windowIcon())
        return editEntry
                
    def __exportBibtex(self): # some stupid error no clue what is wrong!!
        fileName = QtWidgets.QFileDialog.getSaveFileName(self,"Save Bibtex File", self.bibTexSavePath, "Bib tex file (*.bib)")
        if fileName[0]:         # Only if we actually selected a file
            keywords = self.search.returnSearchList()
            log.info("File to store: ",fileName[0])
            self.bibTexSavePath = os.path.dirname(fileName[0])
            self.database.exportBibtex(self.search.returnSearchList(),fileName[0])

    def __appendBibtex(self):
        fileName = QtWidgets.QFileDialog.getSaveFileName(self,"Save Bibtex File", self.bibTexSavePath, "Bib tex file (*.bib)")
        if fileName[0]:   # Only if we actually selected a file
            keywords = self.search.returnSearchList()
            self.bibTexSavePath = os.path.dirname(fileName[0])
            self.database.appendBibtex(self.search.returnSearchList(),fileName[0])

    def __bibtexfromAux(self):
        # Todo: Create a dialog where we can select which fields to export
        fileNameToLoad = QtWidgets.QFileDialog.getOpenFileName(self,"Aux-file to generate Bibtex", self.bibTexSavePath,"aux file (*.aux)")
        if not fileNameToLoad[0]:   # Only if we actually selected a file
            return
        self.bibTexSavePath = os.path.dirname(fileNameToLoad[0])
        try:
            # These go in pypaperdb.cfg as bibtexExcludedFields = url =, author =,...
            excludedTags = tuple(custom.config.get('bibtex','bibtexExcludedFields').split(','))
        except:
            excludedTags = tuple()
            log.warning("No bibtexExcludedFields defined under [bibtex] in pypaperdb.cfg")

        options = {"excludedTags": excludedTags,"month_as_string":['','1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11','12']}
        self.database.writeBibtexFromAux(fileNameToLoad[0],options)

        
    def __writeWindowSettings(self):
        # Function to store the current window's location and geometry
        self.settings = QtCore.QSettings("Hest and Co", "PyPaperDB")
        self.settings.beginGroup("MainWindow")
        self.settings.setValue("geometry",self.saveGeometry())
        self.settings.endGroup()

    def __readWindowSettings(self):
        # Function to restore the current window's location and geometry
        self.settings = QtCore.QSettings("Hest and Co", "PyPaperDB")
        self.settings.beginGroup("MainWindow")
        self.restoreGeometry(self.settings.value("geometry"))
        self.settings.endGroup()

    def editEnded(self,entryId):
        log.info('Edit entry finished with ID ' + str(entryId))
        self.entriesEditedHandles.pop(entryId,None) 

    def editIdChanged(self,oldId,newId):
        log.info('Edit entry ID changed from ' + str(oldId) + ' to ' + str(newId))
        self.entriesEditedHandles[oldId][1] = newId
        return
        
        
    def closeEvent(self, event):
        # When exiting, store window settings
        if bool(self.entriesEditedHandles) is True: # check if the set is empty
            # If true, we are still editing entries
            log.warning(str(self.entriesEditedHandles))
            entryId = list(self.entriesEditedHandles.keys())[0]
            self.entriesEditedHandles[entryId][0].showNormal()
            self.entriesEditedHandles[entryId][0].activateWindow()
            event.ignore()
            return
        
        self.__writeWindowSettings()
        QtWidgets.QMainWindow.closeEvent(self, event)

        
def make_entries_visible(layout,start,end):

    number = 0
    for w in layout_widgets(layout):
        if number <= end and number >= start:
            w.show()
        else:
            w.hide()
        number = number +1
    log.debug('make_entries_visible start ' + str(start) + ' end ' + str(end))
                
def layout_widgets(layout):
   return (layout.itemAt(i).widget() for i in range(layout.count()))



class QEntryArea(QtWidgets.QScrollArea):
    
    def __init__(self,parent=None):
        QtWidgets.QScrollArea.__init__(self,parent)
        self.startVisibleEntries = 0
        self.endVisibleEntries = 25
        self.totalVerticalScroll = 0
        log =logging.getLogger(__name__)
        
    def scrollContentsBy(self,dx,dy):
        #keep behaviour for horizontal scroll
        QtWidgets.QScrollArea.scrollContentsBy(self,dx,0)
       
        if dy == 0:
            log.info("do nothing")
        else:
            self.totalVerticalScroll = self.totalVerticalScroll - dy;
            #print(self.totalVerticalScroll)
            # if(self.startVisibleEntries == int(self.totalVerticalScroll / 300)):
            #     self.startVisibleEntries = int(self.totalVerticalScroll / 300)
            #     #self.endVisibleEntries = self.startVisibleEntries + 5
            # else:
            #     #currentPosition = self.verticalScrollBar().value()
            #     #print(self.verticalScrollBar().maximum())
            #     self.startVisibleEntries = int(self.totalVerticalScroll / 300)
            #     self.endVisibleEntries = self.startVisibleEntries + 5
            self.endVisibleEntries = int(self.totalVerticalScroll/100) + 25
            # self.startVisibleEntries = min(self.startVisibleEntries,int(self.totalVerticalScroll/100))
           
            #print(self.totalVerticalScroll)
            #print(self.startVisibleEntries)
            #print(self.endVisibleEntries)
            make_entries_visible(self.widget().layout(),self.startVisibleEntries,self.endVisibleEntries)
        
        # print('dy ' + str(dy) + ', scroll position '+ str(self.totalVerticalScroll) + ', endVisibleEntries ' + str(self.endVisibleEntries) + ', startVisibleEntries ' + str(self.startVisibleEntries) + ', maximum ' + str(self.verticalScrollBar().maximum()) + ', totalVerticalScroll ' + str(self.totalVerticalScroll) + ', minimum ' + str(self.verticalScrollBar().minimum()))

class Timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            log.info('elapsed time: %f ms' + str(self.msecs))


if __name__ == "__main__":
    # Someone launches this class directly
    print("please run application to start Paperdatabase")
