
import sys,os
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore




class pdfButton(QtWidgets.QPushButton):

    pdfFilePath = None
    dragStartPosition = None

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        super(pdfButton, self).mousePressEvent(event)

        
    def mouseMoveEvent(self,e):
        if e.buttons() != QtCore.Qt.LeftButton:
            return

        if not self.pdfFilePath.endswith('.pdf'):
            return

        print(self.pdfFilePath)

        self.moveBytearray(e)
        return
        mimeData = QtCore.QMimeData()
        # mimeData.setText(self.pdfFilePath)
        # mimeData.setData("application/pdf", "file:///" + self.pdfFilePath)
        # mimeData.setData( "application/pdf",  self.pdfFilePath)
        # mimeData.setUrls([QtCore.QUrl("file:///" + self.pdfFilePath)])
        mimeData.setData('text/uri-list','file:///' + self.pdfFilePath)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos())
        
        dropAction = drag.exec_(QtCore.Qt.CopyAction, QtCore.Qt.CopyAction)
        # dropAction = QtCore.DropAction
        # dropAction = drag.exec_(QtCore.Qt.CopyAction |QtCore.Qt.MoveAction| QtCore.Qt.LinkAction,QtCore.Qt.CopyAction)
        # start the drag operation
        # exec_ will return the accepted action from dropEvent
        # if drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction) == QtCore.Qt.CopyAction:
        
    def moveBytearray(self,e):
        data = QtCore.QByteArray();
        f = QtCore.QFile(self.pdfFilePath)
        if not f.open(QtCore.QIODevice.ReadOnly):
            print('Could not open file: ' + self.pdfFilePath)
            return
        data = f.readAll()
        f.close()

        mimeData = QtCore.QMimeData()
        # mimeData.setData('text/uri-list',QtCore.QUrl('file:///' + self.pdfFilePath))
        mimeData.setUrls([QtCore.QUrl("file:///" + self.pdfFilePath)])
        # mimeData.setText(self.pdfFilePath)
        mimeData.setData('application/pdf',data)
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(e.pos())
        
        dropAction = drag.exec_(QtCore.Qt.CopyAction, QtCore.Qt.CopyAction)
     
        
    def dropEvent(self,e):
        source = e.source()
        print("copy")
        if source != self:
            e.setDropAction(QtCore.CopyAction)
            e.accept()

    def setPdfFilePath(self,filePath):
        self.pdfFilePath = filePath
        
