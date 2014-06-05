#!/usr/bin/env python
#coding: utf-8

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

class Preview (QtGui.QDockWidget):

	def __init__(self, title, context, signals, Parent=None):

		super(Preview, self).__init__(title, Parent)

		self.context = context
		self.signals = signals
		self.parent = Parent
		self.setAllowedAreas(Qt.RightDockWidgetArea)
		self.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)

		self.label = QtGui.QLabel()
		if self.context.getCurrentImagePos() != -1:
			self.label.setPixmap(QtGui.QPixmap.fromImage(self.context.currentQImage()))
		self.label.setObjectName("Preview")
		self.label.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
		self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		self.setWidget(self.label)
		self.update()

		self.signals.updateCanvas.connect(self.update)
		self.signals.imageChanged.connect(self.update)

	def update(self):

		super(Preview, self).update()
		if self.context.currentImage() != None:
			if self.context.currentQImage().width() > 128 or self.context.currentQImage().height() > 128:
				imatge = self.context.currentQImage().scaled(128, 128, Qt.KeepAspectRatio)
				self.label.setPixmap(QtGui.QPixmap.fromImage(imatge))
			else:
				self.label.setPixmap(QtGui.QPixmap.fromImage(self.context.currentQImage()))
		else:
			self.label = QtGui.QLabel()
			self.label.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
			self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
			self.setWidget(self.label)