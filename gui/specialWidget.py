from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets


# Specially defiend widgets
if __name__ == "__main__":
    # Someone launches this class directly
    print("please run application to start Paperdatabase")

class QLabelClickable(QtWidgets.QLabel):

    clicked = QtCore.pyqtSignal()
    
    def __init__(self,title,parent):
        QtWidgets.QLabel.__init__(self,title,parent)
        
    def mouseReleaseEvent(self,event):
        # self.emit(QtCore.SIGNAL("clicked()"))
        self.clicked.emit()


class CopyToClipboardLabelWidget(QLabelClickable):
    clicked = QtCore.pyqtSignal()

    def __init__(self,text,clipboard,parent):
        QLabelClickable.__init__(self,text,parent)
        self.clipboardText = clipboard
        
    def mouseReleaseEvent(self,event):
        # self.emit(QtCore.SIGNAL("clicked()"))
        self.clicked.emit()

    def getClipboardtext(self):
        return self.clipboardText
                
        
    
