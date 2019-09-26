from PyQt5 import QtGui, QtCore, QtWidgets

class EnhancedTextEdit(QtWidgets.QTextEdit):
    """Enhanced version of QtWidgets.QTextEdit which has an editingFinished-signal like QLineEdit.
    and some emacs keybindings"""
    editingFinished = QtCore.pyqtSignal()
    moveMode = QtWidgets.QTextCursor.MoveAnchor
    startSelecting = QtCore.pyqtSignal()

    def __init__(self,parent=None):
        QtWidgets.QTextEdit.__init__(self,parent)
        self.changed = False
        self.textChanged.connect(self._handleTextChanged)
        
        self.startSelecting.connect(self._startSelecting)
    def _handleTextChanged(self):
        self.changed = True
        
    def focusOutEvent(self,event):
        if self.changed:
            self.changed = False
            self.editingFinished.emit()
            QtWidgets.QTextEdit.focusOutEvent(self,event)

    def keyPressEvent(self, event):
        

        if event.modifiers() & QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_A:
            # endline
            self.moveCursor(QtWidgets.QTextCursor.StartOfLine,self.moveMode)
            
        elif event.modifiers() & QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_E:
            # start line
            self.moveCursor(QtWidgets.QTextCursor.EndOfLine,self.moveMode)
        elif (event.modifiers() & QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Right):
            # Next word
            self.moveCursor(QtWidgets.QTextCursor.NextWord,self.moveMode)
        elif (event.modifiers() & QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Left):
            # Previous word
            self.moveCursor(QtWidgets.QTextCursor.PreviousWord,self.moveMode)
        elif (event.modifiers() & QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_P) or event.key() == QtCore.Qt.Key_Up:
            # Line up
            self.moveCursor(QtWidgets.QTextCursor.Up,self.moveMode)
        elif (event.modifiers() & QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_N) or event.key() == QtCore.Qt.Key_Down:
            # Line down
            self.moveCursor(QtWidgets.QTextCursor.Down,self.moveMode)
        elif (event.modifiers() & QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_F)  or event.key() == QtCore.Qt.Key_Right:
            # Forward char
            self.moveCursor(QtWidgets.QTextCursor.NextCharacter,self.moveMode)
        elif (event.modifiers() & QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_B)  or event.key() == QtCore.Qt.Key_Left:
            # Previous char
            self.moveCursor(QtWidgets.QTextCursor.PreviousCharacter,self.moveMode)
        elif (event.modifiers() & QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_W) or event.matches(QtWidgets.QKeySequence.Cut):
            # Cut
            self.cut()
            self.moveMode = QtWidgets.QTextCursor.MoveAnchor
        elif (event.modifiers() & QtCore.Qt.MetaModifier and event.key() == QtCore.Qt.Key_W) or event.matches(QtWidgets.QKeySequence.Copy):
            # Copy
            self.copy()
            self.moveMode = QtWidgets.QTextCursor.MoveAnchor
        elif (event.modifiers() & QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Y) or event.matches(QtWidgets.QKeySequence.Paste):
            # Paste
            self.paste()
            self.moveMode = QtWidgets.QTextCursor.MoveAnchor
        elif (event.modifiers() & QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_K):
            # Kill line
            self.moveMode = QtWidgets.QTextCursor.MoveAnchor
            cur = self.textCursor()
            cur.clearSelection()
            self.setTextCursor(cur)
            self.moveCursor(QtWidgets.QTextCursor.EndOfLine,QtWidgets.QTextCursor.KeepAnchor)
            curNew = self.textCursor()
            if cur.position() == curNew.position():
                # If line already killed, remove the newline char
                self.moveCursor(QtWidgets.QTextCursor.Down,QtWidgets.QTextCursor.KeepAnchor)
                self.moveCursor(QtWidgets.QTextCursor.StartOfLine,QtWidgets.QTextCursor.KeepAnchor)

            self.cut()
        elif event.modifiers() & QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Space:
            # Toggle selection mode
            self.startSelecting.emit()
        elif event.modifiers() & QtCore.Qt.ControlModifier and event.modifiers() & QtCore.Qt.ShiftModifier and event.key() == QtCore.Qt.Key_O:
            # Insert newline above
            cur = self.textCursor()
            self.moveCursor(QtWidgets.QTextCursor.StartOfLine)
            curnew = self.textCursor()
            curnew.insertText("\n")
            self.setTextCursor(curnew)
            
            self.setTextCursor(cur)
        elif event.modifiers() & QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_O:
            # Insert newline below
            cur = self.textCursor()
            self.moveCursor(QtWidgets.QTextCursor.EndOfLine)
            curnew = self.textCursor()
            curnew.insertText("\n")
            self.setTextCursor(curnew)
            self.setTextCursor(cur)
        else:
            if not (event.modifiers() & QtCore.Qt.ControlModifier) or (event.modifiers() & QtCore.Qt.MetaModifier) or (event.modifiers() & QtCore.Qt.ShiftModifier):
                # Do not disable selection mode if CTRL, SHIFT or META are touched
                if self.moveMode == QtWidgets.QTextCursor.KeepAnchor:
                    self.moveMode = QtWidgets.QTextCursor.MoveAnchor
            QtWidgets.QTextEdit.keyPressEvent(self,event)
    


    def _startSelecting(self):
        if self.moveMode == QtWidgets.QTextCursor.MoveAnchor:
            self.moveMode = QtWidgets.QTextCursor.KeepAnchor 
        else:
            self.moveMode = QtWidgets.QTextCursor.MoveAnchor
            cur = self.textCursor()
            cur.clearSelection()
            self.setTextCursor(cur)

class CustomCompleter(QtWidgets.QCompleter): 

    def init(self, parent=None): 
        QtWidgets.QCompleter.init(self, parent)

    def pathFromIndex(self, index):
        path = QtWidgets.QCompleter.pathFromIndex(self, index)

        lst = unicode(self.widget().text()).split(',')
        if len(lst) > 1:
            path = '%s, %s' % (','.join(lst[:-1]), path)

        return path

    def splitPath(self, path):
        path = unicode(path.split(',')[-1]).lstrip(' ')
        return [path]
