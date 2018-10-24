#!/usr/bin/env python
#coding: utf-8

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

from canvas import Canvas


class ScrollArea(QtWidgets.QScrollArea):
	"""
	La clase ScrollArea es una derivada de la clase QScrollArea.
	En este widget se pone, centrado, el lienzo del dibujo (Canvas).
	Además, éste es el widget alrededor del cual se centra la MainWindow.
	"""

	def __init__(self, index, context, signals, Parent=None):

		super(ScrollArea,self).__init__(Parent)

		self.context = context
		self.signals = signals
		self.parent = Parent
		self.canvas = Canvas(index, context, signals, self)

		self.index = index

		self.setBackgroundRole(QtGui.QPalette.Dark)
		self.setObjectName("ScrollArea")
		self.setWidget(self.canvas)

		self.signals.zoom.connect(self.calcNewCanvasPosition)
		self.signals.zoom.connect(self.calcNewScrollBarPosition)
		self.signals.imageRemoved.connect(self.setNewIndex)
		self.signals.newImage.connect(self.setNewImageZoom)

		self.startZoom = 0

	def resizeEvent(self, event):

		super(ScrollArea, self).resizeEvent(event)
		self.calcNewCanvasPosition()
		self.calcNewScrollBarPosition()
		if self.startZoom < 2:
			self.startZoom += 1
			self.setNewImageZoom()
		# self.setNewImageZoom() # Zoom dinámico

	def paintEvent(self, event):

		super(ScrollArea, self).paintEvent(event)
		self.calcNewCanvasPosition()

	def calcNewCanvasPosition(self):

		if self.context.imagePos == self.index:

			g = self.frameGeometry()
			w = g.width()
			h = g.height()

			if self.canvas.width() < w:
				self.canvas.move( (w-self.context.getImagePos(self.index).image.width()*self.context.getImagePos(self.index).zoom)/2 , self.canvas.y() )
			if self.canvas.height() < h:
				self.canvas.move( self.canvas.x(), (h-self.context.getImagePos(self.index).image.height()*self.context.getImagePos(self.index).zoom)/2 )

	def calcNewScrollBarPosition(self):

		if self.context.imagePos == self.index:
			self.horizontalScrollBar().setValue((self.horizontalScrollBar().maximum() - self.horizontalScrollBar().minimum()) / 2)
			self.verticalScrollBar().setValue((self.verticalScrollBar().maximum() - self.verticalScrollBar().minimum()) / 2)

	def setNewIndex(self, removedIndex):

		if self.index >= removedIndex:
			self.index -= 1

	def setNewImageZoom(self):

		print("setNewImageZoom")

		g = self.frameGeometry()
		w = g.width()
		h = g.height()

		self.context.images[-1].zoom = min(w/self.context.images[-1].image.width(), h/self.context.images[-1].image.height())
		self.signals.zoom.emit()

	def mousePressEvent(self, event):

		if event.button() == Qt.MiddleButton:
			self.grabPoint = event.pos()
			self.grabPos = self.canvas.pos()

	def mouseMoveEvent(self, event):

		pos = event.pos()
		self.canvas.move(self.grabPos + event.pos() - self.grabPoint)

		"""
		if (self.mapToParent(pos).x() + self.width() - self.grabPoint.x()) > (self.parent.width() ):
			self.canvas.move(self.parent.width()-self.width(), self.y())
		elif (self.mapToParent(pos).x() - self.grabPoint.x()) < 0:
			self.canvas.move(0, self.y())
		if (self.mapToParent(pos).y() + self.height() - self.grabPoint.y()) > (self.parent.height() ):
			self.canvas.move(self.x(), self.parent.height()-self.height())
		elif (self.mapToParent(pos).y() - self.grabPoint.y()) < 0:
			self.canvas.move(self.x(), 0)
		"""


	def wheelEvent(self, event):

		if self.parent.parent.ctrlPressed:
			self.parent.parent.wheelEvent(event)
		else:
			super(ScrollArea, self).wheelEvent(event)
