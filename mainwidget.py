#!/usr/bin/env python
#coding: utf-8

import gc, sys

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

from scrollarea import ScrollArea


class MainWidget(QtWidgets.QTabWidget):

	def __init__(self, context, signals, Parent=None):

		super(MainWidget, self).__init__(Parent)

		self.context = context
		self.signals = signals
		self.parent = Parent

		self.signals.updateCanvas.connect(self.updateIcon)
		self.signals.resizeCanvas.connect(self.updateIcon)
		self.signals.newImage.connect(self.newTab)
		self.signals.fileNameChanged.connect(self.setTabText)

		self.tabBar = TabBar(self)
		self.setTabBar(self.tabBar)
		self.tabBar.middleClicked.connect(self.closeTab)

		self.setTabsClosable(True)

		self.widgets = []

		for i in range(len(self.context.images)):
			self.newTab()

		self.currentChanged.connect(self.context.setCurrentImagePos)
		self.tabCloseRequested.connect(self.closeTab)

	def newTab(self):

		scrollArea = ScrollArea(self.count(), self.context, self.signals, self)
		scrollArea.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		self.widgets.append(scrollArea)
		self.addTab(scrollArea, "Image" + str(self.count()+1))
		self.setCurrentIndex(self.count()-1)
		self.context.setCurrentImagePos(self.count()-1)

	def closeTab(self, index):

		print(index)
		if self.context.getImagePos(index).modified:
			if self.confirmExit(index): self.removeTab(index)
			return
		self.removeTab(index)

	def removeTab(self, index):

		#print gc.get_referrers(self.widgets[index].canvas)
		#print sys.getrefcount(self.widgets[index].canvas)
		self.context.removeImagePos(index)
		super(MainWidget, self).removeTab(index)
		self.widgets[index].canvas.deleteLater()
		self.widgets[index].canvas = None
		self.widgets[index].deleteLater()
		del self.widgets[index]

	def confirmExit(self, index):

		self.setCurrentIndex(index)
		reply = QtWidgets.QMessageBox.warning(self, self.context.getText("dialog_close_tab", "title"),
			self.context.getText("dialog_close_tab", "message"),
			QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel,
			QtWidgets.QMessageBox.Save)
		if reply == QtWidgets.QMessageBox.Discard:
			return True
		elif reply == QtWidgets.QMessageBox.Cancel:
			return False
		elif reply == QtWidgets.QMessageBox.Save:
			self.parent.saveFile()
			return True

	def updateIcon(self):

		self.setTabIcon(self.currentIndex(), QtGui.QIcon(QtGui.QPixmap.fromImage(self.context.currentQImage())))


class TabBar(QtWidgets.QTabBar):

	middleClicked = QtCore.pyqtSignal(int)
	toBeClosed = 0

	def __init__(self, Parent=None):

		super(TabBar, self).__init__()
		self.parent = Parent
		self.setDrawBase(False) # Fix bug gráfico

	def mousePressEvent(self, event):

		if event.button() == Qt.MidButton:
			self.toBeClosed = self.tabAt(event.pos())

		super(TabBar, self).mousePressEvent(event)

	def mouseReleaseEvent(self, event):

		if event.button() == Qt.MidButton and self.tabAt(event.pos()) == self.toBeClosed:
			self.middleClicked.emit(self.toBeClosed)

		super(TabBar, self).mouseReleaseEvent(event)

	
