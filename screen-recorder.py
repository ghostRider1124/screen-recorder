from PyQt4 import QtCore, QtGui
import sys
import os
import subprocess
import signal
import time


def getDimensions():
	cmd = 'xrandr | grep "\*" | cut -d" " -f4'
	dims = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE).communicate()[0].rstrip('\n')
	return dims


def record(w, h, x, y):
	dims = getDimensions()
	# Dimensions cannot be odd numbers
	if w%2: w+=1
	if h%2: h+=1
	filename = time.strftime("%Y-%m-%d_%H:%M:%s")
	cmd =  ("avconv -f alsa -i pulse -f x11grab -s "+dims+" -r 25 -i :0.0+0,0 -vf crop="+str(w)+":"+str(h)+":"+str(x)+":"+str(y)+
		" -vcodec libx264 -pre:0 lossless_ultrafast  "+filename+".mkv")
	p = subprocess.call(cmd, shell=True)


class ViewSelector(QtGui.QWidget):

	def __init__(self, parent=None):
		super(ViewSelector, self).__init__(parent)
		self.initUI()
		self.setMouseTracking(True)
		self.x = self.xNew = self.y = self.yNew = 0
		self.readyToSelect = False
		self.readyToRecord = False

	def initUI(self):

		self.message = 'Click and drag to select area to record.'

		self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
		
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
		self.setFocusPolicy(QtCore.Qt.StrongFocus)

		self.raise_()
		self.activateWindow()
		self.showFullScreen()

	def mousePressEvent(self, event):
		if not self.readyToSelect:
			self.x = event.pos().x()
			self.y = event.pos().y()
			self.readyToSelect = True
 
	def mouseMoveEvent(self, event):
		if self.readyToSelect:
			self.xNew = event.pos().x()
			self.yNew = event.pos().y()
			self.update()
	
	def mouseReleaseEvent(self, event):
		self.message = 'Press <ENTER> to start recording, <ESC> to cancel or <DELETE> to select again'
		self.update()
		self.readyToSelect = False

	def keyPressEvent(self, qKeyEvent):
		if qKeyEvent.key() == QtCore.Qt.Key_Return:
			self.validateInput()
		elif qKeyEvent.key() == QtCore.Qt.Key_Delete:
			self.message = 'Click and drag to select area to record.'
			self.x = self.y = self.xNew = self.yNew
			self.update()
		elif qKeyEvent.key() == QtCore.Qt.Key_Escape:
			self.close()
	
	def paintEvent(self, event):
		self.drawBox(event)
		p = QtGui.QPainter()
		p.begin(self)
		self.drawText(event, p)
		p.end()

	def closeEvent(self, event):
		self.deleteLater()
		event.accept()

	def drawBox(self, event):
		w = abs(self.xNew - self.x)
		h = abs(self.yNew - self.y)
		x = min(self.x, self.xNew)
		y = min(self.y, self.yNew)
		p = QtGui.QPainter()
		p.begin(self)
		p.setBrush(QtGui.QColor(221,6,90))
		p.setOpacity(0.4)
		p.drawRect(x,y,w,h)
		p.end()

	def drawText(self, event, p):
		p.setPen(QtGui.QColor(80,150,255))
		p.setFont(QtGui.QFont('Decorative', 12))
		p.drawText(event.rect(), QtCore.Qt.AlignCenter, self.message)

	def validateInput(self):
		if abs(self.xNew - self.x) < 100 or abs(self.yNew - self.y) < 100:
			self.message = 'Selected area must be at least 100x100 pixels. Please re-select area to record.'
			self.x = self.y = self.xNew = self.yNew
			self.update()	
		else:	
			w = abs(self.xNew - self.x)
			h = abs(self.yNew - self.y)
			x = min(self.x, self.xNew)
			y = min(self.y, self.yNew)
			self.close()
			record(w, h, x, y)	
	

def appMain():
	app = QtGui.QApplication([])
	app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
	vs = ViewSelector()
	sys.exit(app.exec_())	


if __name__=="__main__":
	appMain()




















