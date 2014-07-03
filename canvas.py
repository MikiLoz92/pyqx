#!/usr/bin/env python
#coding: utf-8

import sys

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

import names as Pixeler
from selection import Selection


class Canvas(QtGui.QLabel):
	"""
	La clase Canvas representa el lienzo donde pintaremos.
	Se expande de tamaño a medida que aumentamos el zoom.
	"""

	def __init__(self, index, context, signals, Parent=None):

		#super(Canvas, self).__init__(QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers), parent)
		super(Canvas, self).__init__(Parent)

		self.setBackgroundRole(QtGui.QPalette.Base)
		self.setAttribute(Qt.WA_TranslucentBackground)
		self.setMouseTracking(True)
		self.setAcceptDrops(True)
		self.setObjectName("Canvas")

		self.signals = signals
		self.signals.zoom.connect(self.zoom)
		self.signals.updateCanvas.connect(self.update)
		self.signals.resizeCanvas.connect(self.resize)
		self.signals.updateTool.connect(self.applySelection)
		self.signals.updateTool.connect(self.changeCursor)
		self.signals.transparentSelection.connect(self.makeSelectionTransparent)
		self.signals.imageRemoved.connect(self.setNewIndex)

		self.signals.cutImage.connect(self.cutImage)
		self.signals.copyImage.connect(self.copyImage)
		self.signals.pasteImage.connect(self.pasteImage)
		self.signals.clearImage.connect(self.clearImage)

		self.parent = Parent
		self.context = context

		self.index = index

		self.setPixmap(QtGui.QPixmap.fromImage(self.context.getImagePos(index).image))

		self.drawing = False
		self.selecting = False
		self.image().selection = None
		#self.toolHint = None

	def image(self):

		return self.context.getImagePos(self.index)

	def setNewIndex(self, removedIndex):

		if self.index >= removedIndex:
			self.index -= 1

	def enterEvent(self, event): # Cuando entra el ratón en el Canvas cambiamos el cursor

		super(Canvas, self).enterEvent(event)
		self.changeCursor()
		self.signals.enterCanvas.emit()

	def leaveEvent(self, event): # Si el ratón se va, lo reiniciamos

		super(Canvas, self).leaveEvent(event)
		self.unsetCursor()
		self.signals.leaveCanvas.emit()

	def changeCursor(self):

		cursors = [0, 0, self.context.pencilCur, self.context.eraserCur, self.context.colorPickerCur, self.context.fillCur, 0, 0]

		for i in range(len(cursors)):
			if self.context.currentTool == i:
				if cursors[i] == 0:
					self.unsetCursor()
				else:
					self.setCursor(cursors[i])
	"""
	def dragEnterEvent(self, event):

		event.acceptProposedAction()
		print event.mimeData()

	def dragMoveEvent(self, event):

		event.acceptProposedAction()

	def dropEvent(self, event):

		mimeData = event.mimeData()
		if mimeData.hasImage() and not mimeData.imageData().isNull():
			self.image().image =  QtGui.QImage(mimeData.imageData())
			self.signals.updateCanvas.emit()
			self.signals.resizeCanvas.emit()
		event.acceptProposedAction()
	"""
	def mousePressEvent(self, event):

		pos = event.pos()
		x = pos.x() / self.image().zoom # x de la imagen
		y = pos.y() / self.image().zoom # y de la imagen

		# Selección
		if self.context.currentTool == Pixeler.Tools.Selection:
			if event.button() == Qt.LeftButton:
				if not self.image().selection:
					# Crear una nueva selección
					self.image().selection = Selection(QtCore.QPoint(x, y), self.context, self)
				else:
					if self.image().selection.rect.contains(QtCore.QPoint(x, y)):
						# Mover selección
						self.image().selection.moving = True
						#self.image().selectionGrabPoint = pos
						self.image().selectionGrabPoint = QtCore.QPoint(x - self.image().selection.rect.x(), y - self.image().selection.rect.y())
					else:
						if self.image().selection.image != None:
							# Pintamos la imagen seleccionada en la imagen final
							self.applySelection()
						self.image().selection = Selection(QtCore.QPoint(x, y), self.context, self)
			elif event.button() == Qt.RightButton:
				pass

		# Lápiz
		elif self.context.currentTool == Pixeler.Tools.Pencil:
			self.lastPoint = QtCore.QPoint(x,y)
			if self.drawing:
				self.drawing = False
				self.image().image =  QtGui.QImage(self.image().history[self.image().posHistory])
			elif event.button() == Qt.LeftButton or event.button() == Qt.RightButton:
				color = self.context.primaryColor if event.button() == Qt.LeftButton else self.context.secondaryColor
				size = self.context.pencilSize
				if event.button() == Qt.RightButton and self.context.secondaryColorEraser:
					color = self.image().bgColor
					size = self.context.eraserSize
				self.image().paintPoint(x, y, color, self.context.pencilSize)
				self.drawing = True
			self.signals.updateCanvas.emit()

		# Goma
		elif self.context.currentTool == Pixeler.Tools.Eraser:
			if event.button() == Qt.LeftButton or event.button() == Qt.RightButton:
				self.lastPoint = QtCore.QPoint(x,y)
				self.image().paintPoint(x, y, self.image().bgColor, self.context.eraserSize)
				self.signals.updateCanvas.emit()
				self.drawing = True

		# Pipeta de color
		elif self.context.currentTool == Pixeler.Tools.ColorPicker:
			if event.button() == Qt.LeftButton:
				self.context.changePrimaryColor( QtGui.QColor(self.context.currentQImage().pixel(QtCore.QPoint(x,y))) )
			elif event.button() == Qt.RightButton:
				self.context.changeSecondaryColor( QtGui.QColor(self.context.currentQImage().pixel(QtCore.QPoint(x,y))) )
			self.signals.updateColor.emit()

		# Cubo
		elif self.context.currentTool == Pixeler.Tools.Fill:
			if event.button() == Qt.LeftButton:
				self.fillImage( (x, y), self.context.primaryColor, self.context.currentQImage().pixel(x,y), self.context.currentQImage() )
			elif event.button() == Qt.RightButton:
				self.fillImage( (x, y), self.context.secondaryColor, self.context.currentQImage().pixel(x,y), self.context.currentQImage() )
			self.image().addHistoryStep()
			self.signals.updateCanvas.emit()

		# Degradado
		elif self.context.currentTool == Pixeler.Tools.Gradient:
			if event.button() == Qt.LeftButton:
				self.context.gradient = Selection(QtCore.QPoint(x, y), self.context, self)

		# Mover canvas
		if event.button() == Qt.MiddleButton:
			self.grabPoint = event.pos()

		self.update()

		# DEBUG
		# print self.width(), self.height()
		# print self.context.currentQImage().width(), self.context.currentQImage().height()
		# print x,y

	def mouseMoveEvent(self, event):

		pos = event.pos()
		x = pos.x() / self.image().zoom # x de la imagen
		y = pos.y() / self.image().zoom # y de la imagen

		self.signals.overCanvas.emit(x, y)

		# Selección
		if self.context.currentTool == Pixeler.Tools.Selection:
			if event.buttons() == Qt.LeftButton:
				if not self.image().selection.finished:
					self.selecting = True
					self.resizeSelection(self.image().selection, event.pos().x(), event.pos().y())
				if self.image().selection.moving:
					self.moveSelection(event.pos().x(), event.pos().y())

		# Lápiz
		elif self.context.currentTool == Pixeler.Tools.Pencil:
			endPoint = QtCore.QPoint(x,y)
			if event.buttons() == Qt.LeftButton and self.drawing:
				self.drawLineTo(QtCore.QPoint(x,y), self.context.primaryColor, self.context.pencilSize)
				self.signals.updateCanvas.emit()
				self.lastPoint = QtCore.QPoint(endPoint)
			elif event.buttons() == Qt.RightButton and self.drawing:
				color = self.context.secondaryColor
				if self.context.secondaryColorEraser:
					color = self.image().bgColor
				self.drawLineTo(QtCore.QPoint(x,y), color, self.context.pencilSize)
				self.signals.updateCanvas.emit()
				self.lastPoint = QtCore.QPoint(endPoint)

		# Goma
		elif self.context.currentTool == Pixeler.Tools.Eraser:
			if event.buttons() == Qt.LeftButton or event.buttons() == Qt.RightButton:
				endPoint = QtCore.QPoint(x,y)
				self.drawLineTo(QtCore.QPoint(x,y), self.image().bgColor, self.context.eraserSize)
				self.signals.updateCanvas.emit()
				self.lastPoint = QtCore.QPoint(endPoint)

		# Degradado
		if self.context.currentTool == Pixeler.Tools.Gradient:
			if event.buttons() == Qt.LeftButton:
				if self.context.gradient and not self.context.gradient.finished:
					self.selecting = True
					self.resizeSelection(self.context.gradient, event.pos().x(), event.pos().y())

		if event.buttons() == Qt.MiddleButton:
			
			self.move(self.mapToParent(event.pos() - self.grabPoint))

			w = self.parent.frameGeometry().width()
			h = self.parent.frameGeometry().height()

			sb = self.parent.horizontalScrollBar()
			"""
			sb.maximum() - sb.minimum() -> self.mapToParent(self.pos().x()) - self.frameGeometry().width()
			sb.value() -> x
			"""
			sb.setValue( self.mapToParent(self.pos()).x() * sb.maximum() / float(-self.width() + self.parent.width())  )

		self.update()

	def drawToolHint(self, x, y):

		if self.context.currentTool == Pixeler.Tools.Pencil: m = self.context.circles[self.context.pencilSize-1]
		elif self.context.currentTool == Pixeler.Tools.Eraser: m = self.context.circles[self.context.eraserSize-1]

		painter = QtGui.QPainter(self)
		#painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
		pen = QtGui.QPen(QtGui.QColor(0,0,0,96))
		#pen.setStyle(Qt.DotLine)
		painter.setPen(pen)
		size = len(m)

		for i in range(size):
			for j in range(size):
				if m[i][j]:
					if j == 0 or not m[i][j-1]:
						x0 = (x-size/2+j)*self.image().zoom
						y0 = (y-size/2+i)*self.image().zoom
						y1 = (y-size/2+i+1)*self.image().zoom-1
						painter.drawLine(x0, y0, x0, y1)
					if j == size-1 or not m[i][j+1]:
						x0 = (x+size/2+(j-size)+2)*self.image().zoom-1
						y0 = (y-size/2+i)*self.image().zoom
						y1 = (y-size/2+i+1)*self.image().zoom-1
						painter.drawLine(x0, y0, x0, y1)
					if i == 0 or not m[i-1][j]:
						x0 = (x-size/2+j)*self.image().zoom
						x1 = (x-size/2+j+1)*self.image().zoom-1
						y0 = (y-size/2+i)*self.image().zoom
						painter.drawLine(x0, y0, x1, y0)
					if i == size-1  or not m[i+1][j]:
						x0 = (x+size/2+(j-size)+1)*self.image().zoom
						x1 = (x+size/2+(j-size)+2)*self.image().zoom-1
						y0 = (y+size/2+(i-size)+2)*self.image().zoom-1
						painter.drawLine(x0, y0, x1, y0)
			
	def mouseReleaseEvent(self, event):

		pos = event.pos()
		x = pos.x() / self.image().zoom # x de la imagen
		y = pos.y() / self.image().zoom # y de la imagen

		# Selección
		if self.context.currentTool == Pixeler.Tools.Selection and event.button() == QtCore.Qt.LeftButton:
			
			if self.selecting:
				print "Selection made starting at (" + str(self.image().selection.origin.x()) + ", " + str(self.image().selection.origin.y()) + ") and ending at (" + str(x) + ", " + str(y) + ") (both included)"
				print self.image().selection
				self.image().selection.originTopLeft = QtCore.QPoint(self.image().selection.rect.x(), self.image().selection.rect.y())
				self.image().selection.finished = True
				self.image().selection.image = self.context.currentQImage().copy(self.image().selection.rect)
				self.makeSelectionTransparent(self.context.transparentSelection)
				print self.image().selection.image
				painter = QtGui.QPainter(self.context.currentQImage())
				painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
				painter.fillRect(self.image().selection.rect, self.image().bgColor)
			else:
				if self.image().selection != None and self.image().selection.finished:
					print "Moved selection"
					pass
				else:
					print "No selection was made"
					self.image().selection = None
			self.selecting = False

		# Lápiz
		elif self.context.currentTool == Pixeler.Tools.Pencil and self.drawing:
			if event.button() == Qt.LeftButton or event.button() == Qt.RightButton:
				self.image().addHistoryStep()
				self.drawing = False

		# Goma
		elif self.context.currentTool == Pixeler.Tools.Eraser:
			if event.button() == Qt.LeftButton or event.button() == Qt.RightButton:
				self.image().addHistoryStep()
				self.drawing = False

		# Degradado
		if self.context.currentTool == Pixeler.Tools.Gradient and event.button() == QtCore.Qt.LeftButton:
			
			if self.selecting:
				#print "Gradient made starting at (" + str(self.context.gradient.origin.x()) + ", " + str(self.context.gradient.origin.y()) + ") and ending at (" + str(x) + ", " + str(y) + ") (both included)"
				x1,y1 = self.context.gradient.origin.x(), self.context.gradient.origin.y()
				x2,y2 = x,y
				xm,ym = max(x1,x2),max(y1,y2)
				if xm == x2 : 
					lx = range(x1,x2+1)
				else:
					lx = range(x1,x2-1,-1)
				if ym == y2:
					ly = range(y1,y2+1)
				else:
					ly = range(y1,y2-1,-1)
				self.context.gradient.originTopLeft = QtCore.QPoint(self.context.gradient.rect.x(), self.context.gradient.rect.y())
				self.context.gradient.finished = True
				self.context.gradient.image = self.context.currentQImage().copy(self.context.gradient.rect)
				self.context.gradient.hide()
				self.context.gradient = None
				# OPERACIONES DE PINTADO AQUí ABAJO
				painter = QtGui.QPainter(self.context.currentQImage())
				painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
				#painter.fillRect(x1,y1,x2,y2, self.image().bgColor)
				if self.context.DegState == 2:
					if self.context.DegDir == 'H':
						for i in ly:
							self.Grad2Colors( (x1,i) , (x2,i) )
					else:
						for i in lx:
							self.Grad2Colors( (i,y1) , (i,y2) )
				elif self.context.DegState == 1:
					if self.context.DegDir == 'H':
						for i in ly:
							self.GradColorAlpha( (x1,i) , (x2,i) )
					else:
						for i in lx:
							self.GradColorAlpha( (i,y1) , (i,y2) )
				self.image().addHistoryStep()
				self.signals.updateCanvas.emit()

			self.selecting = False
	
	def paintEvent(self, event):
		
		#super(Canvas, self).paintEvent(event)

		painter = QtGui.QPainter(self)

		# Transparency
		if self.image().bgColor == QtGui.QColor(0,0,0,0):
			painter.fillRect(self.rect(), QtGui.QBrush(QtGui.QImage("images/transparent.png")))
		
		# Image
		painter.drawImage(self.rect(), self.context.currentQImage())

		# Selection
		if not self.selecting and self.image().selection != None and self.image().selection.finished and self.image().selection.image != None:
			rect = QtCore.QRect(self.image().selection.rect.topLeft()*self.image().zoom, self.image().selection.rect.size()*self.image().zoom)
			painter.drawImage(rect, self.image().selection.image)

		# Pixel Grid
		if self.context.grid and self.image().zoom > 3:
			r = self.image().bgColor.red()
			g = self.image().bgColor.green()
			b = self.image().bgColor.blue()
			gridColor = QtGui.QColor(255-r, 255-g, 255-b, 128)
			pen = QtGui.QPen(gridColor)
			if self.image().zoom < 9:
				pen.setStyle(Qt.SolidLine)
			else:
				pen.setStyle(Qt.DotLine)
			painter.setPen(pen)
			w = self.context.currentQImage().width()
			h = self.context.currentQImage().height()
			for i in range(w)[1:]:
				painter.drawLine(i*self.image().zoom-1, 0, i*self.image().zoom-1, h*self.image().zoom)
			for i in range(h)[1:]:
				painter.drawLine(0, i*self.image().zoom-1, w*self.image().zoom, i*self.image().zoom-1)

		# Matrix Grid
		if self.context.matrixGrid and self.image().zoom >= 3:
			painter.setPen(QtGui.QColor(127,67,167,128))
			w = self.context.currentQImage().width()
			h = self.context.currentQImage().height()
			for i in range(w)[1:]:
				if i % self.context.matrixGridWidth == 0:
					painter.drawLine(i*self.image().zoom, 0, i*self.image().zoom, h*self.image().zoom)
			for i in range(h)[1:]:
				if i % self.context.matrixGridHeight == 0:
					painter.drawLine(0, i*self.image().zoom, w*self.image().zoom, i*self.image().zoom)

		if self.context.currentTool == Pixeler.Tools.Pencil or self.context.currentTool == Pixeler.Tools.Eraser:
			# Draw ToolHint
			xcursor = self.mapFromGlobal(QtGui.QCursor().pos()).x()/self.image().zoom
			ycursor = self.mapFromGlobal(QtGui.QCursor().pos()).y()/self.image().zoom
			self.drawToolHint(xcursor, ycursor)

	def makeSelectionTransparent(self, x):

		if self.context.imagePos == self.index and self.image().selection != None:
			if x:
				fromColor = self.image().bgColor
				toColor = QtGui.QColor(0,0,0,0)
			else:
				fromColor = QtGui.QColor(0,0,0,0)
				toColor = self.image().bgColor

			image = self.image().selection.image
			mask = QtGui.QPixmap.fromImage(image).createMaskFromColor(fromColor, QtCore.Qt.MaskOutColor)
			painter = QtGui.QPainter(image)
			painter.setPen(toColor)
			painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
			painter.drawPixmap(image.rect(), mask, mask.rect())
			painter.end()

	def zoom(self): # Cosas que hacer cuando se aplica un zoom

		if self.image().selection != None: # Calcular la nueva geometría de la selección, en caso que haya
			self.calcNewSelectionGeometry()
		self.resize()

	def resize(self):

		super(Canvas, self).resize(QtCore.QSize(self.image().image.width()*self.image().zoom, self.image().image.height()*self.image().zoom))
	
	def drawLineTo(self, endPoint, color, size):

		steep = 0

		dx = abs(endPoint.x() - self.lastPoint.x())
		if (endPoint.x() - self.lastPoint.x()) > 0: sx = 1
		else: sx = -1

		dy = abs(endPoint.y() - self.lastPoint.y())
		if (endPoint.y() - self.lastPoint.y()) > 0: sy = 1
		else: sy = -1

		x = self.lastPoint.x()
		y = self.lastPoint.y()

		if dy > dx:
		    steep = 1
		    x,y = y,x
		    dx,dy = dy,dx
		    sx,sy = sy,sx
		d = (2 * dy) - dx

		for i in range(0,dx):
		    if steep: self.image().paintPoint(y, x, color, size)
		    else: self.image().paintPoint(x, y, color, size)
		    while d >= 0:
		        y = y + sy
		        d = d - (2 * dx)
		    x = x + sx
		    d = d + (2 * dy)

		self.image().paintPoint(endPoint.x(), endPoint.y(), color, size)

	def applySelection(self):

		if self.image().selection != None:
			print "Applying selection"
			painter = QtGui.QPainter(self.image().image)
			painter.drawImage(self.image().selection.rect.topLeft(), self.image().selection.image)
			if self.image().selection.originTopLeft != self.image().selection.rect.topLeft():
				self.image().addHistoryStep()
			self.signals.updateCanvas.emit()
			self.image().selection.hide()
			self.image().selection = None

	def cutImage(self):

		if self.context.imagePos == self.index: # Cortar sólo si este Canvas es el actual
			clipboard = QtGui.QApplication.clipboard()
			if self.image().selection != None:
				clipboard.setImage(self.image().selection.image)
				self.image().selection.hide()
				self.image().selection = None
				self.image().addHistoryStep()
				self.signals.updateCanvas.emit()

	def copyImage(self):

		if self.context.imagePos == self.index: # Copiar sólo si este Canvas es el actual
			clipboard = QtGui.QApplication.clipboard()
			if self.image().selection != None:
				clipboard.setImage(self.image().selection.image)

	def pasteImage(self):

		print "imagePos: ", self.context.imagePos, ", self.index: ", self.index
		if self.context.imagePos == self.index: # Pegar sólo si este Canvas es el actual
			print "Pasting image"
			self.signals.autoUpdateTool.emit(0)
			self.applySelection()
			image = QtGui.QApplication.clipboard().image()
			self.image().selection = Selection(QtCore.QPoint(0,0), self.context, self)
			self.image().selection.setGeometry(0, 0, image.width(), image.height())
			self.image().selection.image = image
			self.image().selection.show()
			self.image().selection.finished = True
			self.makeSelectionTransparent(self.context.transparentSelection)

	def clearImage(self):

		print "Borrando"
		if self.context.imagePos == self.index: # Eliminar sólo si este Canvas es el actual

			if self.image().selection != None:
				self.image().selection.hide()
				self.image().selection = None
				self.image().addHistoryStep()
				self.signals.updateCanvas.emit()

	def resizeToNewImage(self):

		if self.image().selection != None:
			self.image().selection.hide()
			self.image().selection = None
		self.resize()
		self.setPixmap(QtGui.QPixmap.fromImage(self.image().image))
		self.signals.updateCanvas.emit()

	def fillImage(self, begin, paint, current, imagen):

		if paint.rgb() == current :
			#print "pass activated"
			pass
		else:
			queue = [begin]
			for x,y in queue:
				if imagen.pixel(x,y) == current:
					cond = True
					nodes = [(x,y)]
					xt = x-1
					while xt>=0 and cond: 
						cond = imagen.pixel(xt,y)==current
						if cond:
							nodes.append( (xt,y) ) 
							xt = xt-1

					cond = True
					xt = x+1
					while xt<imagen.width() and cond : 
						cond = imagen.pixel(xt,y)==current
						if cond:
							nodes.append( (xt,y) ) 
							xt = xt+1

					for xp,yp in nodes:
						imagen.setPixel(xp,yp,paint.rgb())
						if yp<imagen.width()-1:
							if imagen.pixel(xp,yp+1) == current: 
								queue.append( (xp,yp+1) )
						if yp>0:
							if imagen.pixel(xp,yp-1) == current:
								queue.append( (xp,yp-1) )

	def Grad2Colors(self, pi, pf):

		alpha = self.context.DegAlpha

		if pf[0] == pi[0]:

			Var_y = pf[1] - pi[1]
			if Var_y > 0 :
				dy = +1
			elif Var_y < 0 :
				dy = -1
			else:
				return 0

			color1 = self.context.primaryColor.getRgb()
			color2 = self.context.secondaryColor.getRgb()
			#print color1,color2

			Var_r = color2[0] - color1[0]
			dr = float(Var_r)/abs(Var_y)
			Var_g = color2[1] - color1[1]
			dg = float(Var_g)/abs(Var_y)
			Var_b = color2[2] - color1[2]
			db = float(Var_b)/abs(Var_y)
			#print dr, dg, db

			for i in range(0,abs(Var_y)+1):
				R = color1[0] + i*dr
				G = color1[1] + i*dg
				B = color1[2] + i*db
				R = int( round(R) )
				G = int( round(G) )
				B = int( round(B) )
				#print R,G,B

				tmp_c = QtGui.QColor(R,G,B,alpha)
				#print "changed color"
				self.context.currentQImage().setPixel(pi[0],pi[1]+i*dy,tmp_c.rgba())

			return 0

		elif pf[1] == pi[1]:

			Var_x = pf[0] - pi[0]
			if Var_x > 0 :
				dx = +1
			elif Var_x < 0 :
				dx = -1
			else:
				return 0

			color1 = self.context.primaryColor.getRgb()
			color2 = self.context.secondaryColor.getRgb()
			#print color1,color2

			Var_r = color2[0] - color1[0]
			dr = float(Var_r)/abs(Var_x)
			Var_g = color2[1] - color1[1]
			dg = float(Var_g)/abs(Var_x)
			Var_b = color2[2] - color1[2]
			db = float(Var_b)/abs(Var_x)
			#print dr, dg, db

			for i in range(0,abs(Var_x)+1):
				R = color1[0] + i*dr
				G = color1[1] + i*dg
				B = color1[2] + i*db
				R = int( round(R) )
				G = int( round(G) )
				B = int( round(B) )
				#print R,G,B

				tmp_c = QtGui.QColor(R,G,B,alpha)
				self.context.currentQImage().setPixel(pi[0]+i*dx,pi[1],tmp_c.rgba())
			return 0

		else:
			return 1

	def GradColorAlpha(self, pi, pf):

		alpha = self.context.DegAlpha

		if pf[0] == pi[0]:

			Var_y = pf[1] - pi[1]
			if Var_y > 0 :
				dy = +1
			elif Var_y < 0 :
				dy = -1
			else:
				return 0

			color = self.context.primaryColor
			da = 255/abs(Var_y)

			for i in range(0,abs(Var_y)+1):

				color.setAlpha(255-da*i)
				#print "changed color"
				self.context.currentQImage().setPixel(pi[0],pi[1]+i*dy,color.rgba())

			return 0

		elif pf[1] == pi[1]:

			Var_x = pf[0] - pi[0]
			if Var_x > 0 :
				dx = +1
			elif Var_x < 0 :
				dx = -1
			else:
				return 0

			color = self.context.primaryColor
			da = 255/abs(Var_x)

			for i in range(0,abs(Var_x)+1):

				color.setAlpha(255-da*i)
				self.context.currentQImage().setPixel(pi[0]+i*dx,pi[1],color.rgba())

			return 0

		else:
			return 1

	def resizeSelection(self, selection, xevent, yevent):

		# En la imagen
		x = xevent / self.image().zoom
		y = yevent / self.image().zoom

		if x >= selection.origin.x() and y >= selection.origin.y():
			selection.setGeometry( selection.origin.x(), selection.origin.y(), x - selection.origin.x() + 1, y - selection.origin.y() + 1 )
		elif x < selection.origin.x() and y >= selection.origin.y():
			selection.setGeometry( x, selection.origin.y(), selection.origin.x() - x + 1, y - selection.origin.y() + 1 )
		elif x < selection.origin.x() and y < selection.origin.y():
			selection.setGeometry( x, y, selection.origin.x() - x + 1, selection.origin.y() - y + 1 )
		elif x >= selection.origin.x() and y < selection.origin.y():
			selection.setGeometry( selection.origin.x(), y, x - selection.origin.x() + 1, selection.origin.y() - y + 1 )
		else:
			selection.setGeometry( xorig, yorig, 1, 1 )

		selection.show()

	def calcNewSelectionGeometry(self):

		if self.image().selection != None and self.image().selection.finished:
			self.image().selection.setGeometry(self.image().selection.rect.x(), self.image().selection.rect.y(), self.image().selection.rect.width(), self.image().selection.rect.height())

	def moveSelection(self, xevent, yevent):

		# En la imagen
		x = xevent / self.image().zoom
		y = yevent / self.image().zoom

		xx = self.image().selectionGrabPoint.x()
		yy = self.image().selectionGrabPoint.y()

		self.image().selection.setGeometry(x - xx, y - yy, self.image().selection.rect.width(), self.image().selection.rect.height())

	def selectAll(self):

		self.signals.autoUpdateTool.emit(0)
		selection = Selection(QtCore.QPoint(0,0), self.context, self)
		selection.setGeometry(0,0,self.image().image.width(), self.image().image.height())
		selection.originTopLeft = QtCore.QPoint(0,0)
		selection.image = QtGui.QImage(self.context.currentQImage())
		self.makeSelectionTransparent(self.context.transparentSelection)
		selection.finished = True
		selection.show()
		self.image().selection = selection
		painter = QtGui.QPainter(self.context.currentQImage())
		painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
		painter.fillRect(self.image().selection.rect, self.image().bgColor)
		painter.end()
