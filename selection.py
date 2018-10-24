#!/usr/bin/env python
#coding: utf-8

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt


class Selection(QtWidgets.QRubberBand):

	def __init__(self, origin, context, Parent=None):

		super(Selection, self).__init__(QtWidgets.QRubberBand.Rectangle, Parent)

		self.context = context

		self.origin = QtCore.QPoint(origin)
		self.originTopLeft = QtCore.QPoint()
		self.finished = False
		self.moving = False
		self.image = None
		self.rect = QtCore.QRect()

	def setGeometry(self, x, y, w, h): # Todos los argumentos son el imagen, no en el Canvas

		self.rect = QtCore.QRect(x, y, w, h)
		super(Selection, self).setGeometry( x * self.context.currentImage().zoom - 1, y * self.context.currentImage().zoom - 1, w * self.context.currentImage().zoom + 2, h * self.context.currentImage().zoom + 2 )
