#!/usr/bin/env python
#coding: utf-8

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
import random


class CurrentColor(QtWidgets.QLabel):

	def __init__(self, primary, context, signals, Parent=None):

		super(CurrentColor, self).__init__()

		self.parent = Parent
		self.context = context
		self.signals = signals
		self.signals.updateColor.connect(self.update)
		self.primary = primary

		if primary:
			self.color = self.context.primaryColor
			self.setObjectName("PrimaryColor")
		else:
			self.color = self.context.secondaryColor
			self.setObjectName("SecondaryColor")

		self.setStyleSheet("background-color: " + self.color.name() + ";")
		self.setFixedHeight(24)

	def mouseMoveEvent(self, e):

		mimecontext = QtCore.QMimeData()
		mimecontext.setColorData(self.color)

		drag = QtWidgets.QDrag(self)
		drag.setMimeData(mimecontext)
		drag.setHotSpot(e.pos() - self.rect().topLeft())

		dropAction = drag.start(QtCore.Qt.MoveAction)

	def mouseReleaseEvent(self, e):

		if e.button() == Qt.LeftButton:
			c = QtWidgets.QColorDialog.getColor(self.color)
			if c.isValid():
				if self.primary: self.context.changePrimaryColor(c)
				else: self.color = self.context.changeSecondaryColor(c)

	def update(self):

		if self.primary:
			self.color = self.context.primaryColor
			self.setStyleSheet("background-color: " + self.color.name() + ";")
		else:
			self.color = self.context.secondaryColor
			self.setStyleSheet("background-color: " + self.color.name() + ";")
		
		super(CurrentColor, self).update()


class Color(QtWidgets.QFrame):
	"""
	Una QFrame cuadrada que representa un color de la paleta.
	"""

	def __init__(self, position, color, context, signals, Parent=None):

		super(Color, self).__init__(Parent)

		self.parent = Parent
		self.context = context
		self.signals = signals

		self.position = position
		self.color = QtGui.QColor(color[0], color[1], color[2])

		self.setObjectName("Color")
		self.setFixedSize(12, 12)
		self.setStyleSheet("background-color: " + self.color.name() + ";")

		self.setAcceptDrops(True)

	def mousePressEvent(self, e):

		if e.button() == Qt.LeftButton:
			self.context.changePrimaryColor(self.color)
		elif e.button() == Qt.RightButton:
			self.context.changeSecondaryColor(self.color)
		elif e.button() == Qt.MidButton:
			c = QtWidgets.QColorDialog.getColor(self.color)
			if c.isValid():
				self.changeColor(c)

	"""
	def mouseMoveEvent(self, e):

		mimecontext = QtCore.QMimecontext()
		mimecontext.setColorcontext(self.color)

		drag = QtWidgets.QDrag(self)
		drag.setMimecontext(mimecontext)
		drag.setHotSpot(e.pos() - self.rect().topLeft())

		dropAction = drag.start(QtCore.Qt.MoveAction)

		self.changeColor(QtWidgets.QColor(0,0,0))
	"""

	def dragEnterEvent(self, e):

		if e.mimeData().hasColor():
			e.accept()

	def dropEvent(self, e):

		self.changeColor(QtWidgets.QColor(e.mimeData().colorData()))

		e.setDropAction(QtCore.Qt.CopyAction)
		e.accept()

	def update(self):

		self.setStyleSheet("background-color: " + self.color.name() + ";")
		super(Color, self).update()

	def changeColor(self, c):

		self.color = c
		self.context.palette[self.position] = [c.red(), c.green(), c.blue()]
		self.update()

class Palette (QtWidgets.QWidget):

	def __init__(self, context, signals, Parent=None):

		super(Palette, self).__init__(Parent)

		self.parent = Parent
		self.context = context
		self.signals = signals
		self.setObjectName("Palette")

		palette = QtWidgets.QGridLayout()
		for i in range(5):
			for j in range(12):
				palette.addWidget(Color(i*12+j, self.context.palette[i*12+j], self.context, self.signals), i, j)
				"""
				if i > 1:
					palette.addWidget(Color(True, self.context, self.signals), i, j)
				else:
					palette.addWidget(Color(False, self.context, self.signals), i, j)
				"""
		palette.setSpacing(1)

		hbox = QtWidgets.QHBoxLayout()
		hbox.addWidget(CurrentColor(True, self.context, self.signals))
		hbox.addWidget(CurrentColor(False, self.context, self.signals))
		hbox.setSpacing(2)
		#hbox.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)

		vbox = QtWidgets.QVBoxLayout()
		vbox.addLayout(hbox)
		vbox.addLayout(palette)
		vbox.setSpacing(2)
		#vbox.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)

		self.setLayout(vbox)
		self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
