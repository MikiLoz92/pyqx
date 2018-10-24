#!/usr/bin/env python
#coding: utf-8

import os

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

import names as Pixeler
from mainwidget import MainWidget
from palette import Palette
from toolproperties import ToolProperties
from preview import Preview
from dialogs import NewFileDialog, ResizeImageDialog, ResizeCanvasDialog, Preferences


class MainWindow(QtWidgets.QMainWindow):

	def __init__(self, context, signals):

		super(MainWindow, self).__init__()

		self.signals = signals
		self.context = context

		self.resize(800,480)
		self.setWindowTitle(self.context.getText("pyqx", "title"))
		
		self.statusBar = self.statusBar()
		self.menuBar = self.createMenuBar()
		self.toolBar = self.createToolBar()
		self.createDockWidgets()

		self.ctrlPressed = False

		self.mainWidget = MainWidget(context, signals, self)
		self.setCentralWidget(self.mainWidget)

		self.imagePosLabel = QtWidgets.QLabel()
		self.imagePosLabel.setObjectName("ImagePosLabel")

		self.signals.autoUpdateTool.connect(self.setCurrentTool)
		self.signals.enterCanvas.connect(self.showImagePosition)
		self.signals.leaveCanvas.connect(self.hideImagePosition)
		self.signals.overCanvas.connect(self.setImagePosition)

		self.show()

	def createPopupMenu(self):

		pass # Reimplementando esta función conseguimos que no se creen los menús popup cuando hacemos click derecho en toolbars/dockwidgets.

	def createToolBarActions(self):

		l = []

		self.tools = QtWidgets.QActionGroup(self)

		tools = ["selection", "magicwand", "pencil", "eraser", "colorpicker", "fill", "gradient", "exchange"]
		connects = [lambda: self.context.changeCurrentTool(Pixeler.Tools.Selection),
					lambda: self.context.changeCurrentTool(Pixeler.Tools.MagicWand),
					lambda: self.context.changeCurrentTool(Pixeler.Tools.Pencil),
					lambda: self.context.changeCurrentTool(Pixeler.Tools.Eraser),
					lambda: self.context.changeCurrentTool(Pixeler.Tools.ColorPicker),
					lambda: self.context.changeCurrentTool(Pixeler.Tools.Fill),
					lambda: self.context.changeCurrentTool(Pixeler.Tools.Gradient),
					lambda: self.context.changeCurrentTool(Pixeler.Tools.Exchange)]
		shortcuts = ['Z', '', 'X', 'C', 'A', 'S', 'D', '']

		for i in range(len(tools)):
			a = QtWidgets.QAction(QtGui.QIcon( os.path.join("themes", self.context.theme, tools[i] + ".png") ), self.context.getText("tools", tools[i]) + " (" + shortcuts[i] + ")", self.tools)
			a.setCheckable(True)
			a.setShortcut(shortcuts[i])
			if connects[i] != 0: a.toggled.connect(connects[i])
			l.append(a)

		a = QtWidgets.QAction(QtGui.QIcon( os.path.join("themes", self.context.theme, "zoomin.png") ), self.context.getText("tools", "zoomin"), self.tools)
		a.setShortcut("Ctrl++")
		a.triggered.connect(self.zoomIn)
		l.append(a)

		a = QtWidgets.QAction(QtGui.QIcon( os.path.join("themes", self.context.theme, "zoomout.png") ), self.context.getText("tools", "zoomout"), self.tools)
		a.setShortcut("Ctrl+-")
		a.triggered.connect(self.zoomOut)
		l.append(a)

		l[self.context.currentTool].setChecked(True)

		return l

	def createToolBar(self):

		toolBar = QtWidgets.QToolBar()
		l = self.createToolBarActions()

		j = 0
		for i in l:
			toolBar.addAction(i)
			if j == 7:
				toolBar.addSeparator()
			j += 1

		toolBar.setMovable(False)
		toolBar.setOrientation(Qt.Vertical)
		self.addToolBar(Qt.LeftToolBarArea, toolBar)

		return toolBar

	def createFileActions(self):

		ids = ["new", "open", "save", "saveas", "exit"]
		icons = ["document-new.png", "document-open.png", "document-save.png", "document-save-as.png", "application-exit.png"]
		shortcuts = ['Ctrl+N', 'Ctrl+O', 'Ctrl+S', 'Ctrl+Shift+S', 'Ctrl+Q']
		connects = [self.newFile, self.openFile, self.saveFile, self.saveFileAs, self.close]

		l = []

		for i in range(len(ids)):
			a = QtWidgets.QAction(QtGui.QIcon("images/" + icons[i]), self.context.getText("menu_file_labels", ids[i]), self)
			a.setShortcut(shortcuts[i])
			a.triggered.connect(self.restoreFocus)
			a.setStatusTip(self.context.getText("menu_file_status_tips", ids[i]))
			if connects[i] != 0: a.triggered.connect(connects[i])
			l.append(a)

		l.insert(4,0) # Los ceros simbolizan separadores

		return l

	def createEditActions(self):

		ids = ["undo", "redo", "selectall", "deselect", "cut", "copy", "paste", "clear", "preferences"]
		icons = ["edit-undo.png", "edit-redo.png", "", "", "edit-cut.png", "edit-copy.png", "edit-paste.png", "edit-clear.png", "document-properties.png"]
		shortcuts = ['Ctrl+Z', 'Ctrl+Y', "Ctrl+A", "Ctrl+Shift+A", 'Ctrl+X', 'Ctrl+C', 'Ctrl+V', 'Del', '']
		connects = [self.undo, self.redo, self.selectAll, self.deselect, self.cut, self.copy, self.paste, self.clear, self.showPreferences]

		l = []

		for i in range(len(ids)):
			a = QtWidgets.QAction(QtGui.QIcon("images/" + icons[i]), self.context.getText("menu_edit_labels", ids[i]), self)
			a.setShortcut(shortcuts[i])
			a.triggered.connect(self.restoreFocus)
			a.setStatusTip(self.context.getText("menu_edit_status_tips", ids[i]))
			if connects[i] != 0: a.triggered.connect(connects[i])
			l.append(a)

		# Los ceros simbolizan separadores
		l.insert(2,0)
		l.insert(5,0)
		l.insert(10,0)

		return l

	def createViewActions(self):

		ids = ["pixel_grid", "matrix_grid"]
		icons = ["", ""]
		shortcuts = ['Ctrl+G', 'Ctrl+M']
		connects = [self.setPixelGrid, self.setMatrixGrid]

		l = []

		for i in range(len(ids)):
			a = QtWidgets.QAction(QtGui.QIcon("images/" + icons[i]), self.context.getText("menu_view_labels", ids[i]), self)
			a.setShortcut(shortcuts[i])
			a.triggered.connect(self.restoreFocus)
			a.setStatusTip(self.context.getText("menu_view_status_tips", ids[i]))
			if connects[i] != 0: a.triggered.connect(connects[i])
			a.setCheckable(True)
			l.append(a)

		l.insert(2,0) # Los ceros simbolizan separadores

		# Algunas opcionas son chekables, lo consideramos:
		l[0].setCheckable(True)
		if self.context.grid: l[0].setChecked(True)
		l[1].setCheckable(True)
		if self.context.matrixGrid: l[1].setChecked(True)

		return l

	def createTransformActions(self):

		ids = ["flip_hor", "flip_ver", "rotate_cw", "rotate_ccw", "rotate_180", "resize", "resize_canvas"]
		icons = ["", "", "", "", "", "", ""]
		shortcuts = ['', '', '', '', '', '', '']
		connects = [self.flipHorizontally,self.flipVertically,self.rotate90CW,self.rotate90CCW,self.rotate180,self.showResizeImageDialog,self.showResizeCanvasDialog]

		l = []

		for i in range(len(ids)):
			a = QtWidgets.QAction(QtGui.QIcon("images/" + icons[i]), self.context.getText("menu_transform_labels", ids[i]), self)
			a.setShortcut(shortcuts[i])
			a.triggered.connect(self.restoreFocus)
			a.setStatusTip(self.context.getText("menu_transform_status_tips", ids[i]))
			if connects[i] != 0: a.triggered.connect(connects[i])
			l.append(a)

		# Los ceros simbolizan separadores
		l.insert(2,0)
		l.insert(6,0)

		return l

	def createHelpActions(self):

		ids = ["contents", "about"]
		icons = ["help-contents.png", "help-about.png"]
		shortcuts = ['F1', 'Ctrl+B']
		connects = [self.showHelp, self.showAboutDialog]

		l = []

		for i in range(len(ids)):
			a = QtWidgets.QAction(QtGui.QIcon("images/" + icons[i]), self.context.getText("menu_help_labels", ids[i]), self)
			a.setShortcut(shortcuts[i])
			a.triggered.connect(self.restoreFocus)
			a.setStatusTip(self.context.getText("menu_help_status_tips", ids[i]))
			if connects[i] != 0: a.triggered.connect(connects[i])
			l.append(a)

		l.insert(1,0) # Los ceros simbolizan separadores

		return l

	def createMenuBar(self):
		
		menubar = self.menuBar()
		fileMenu = menubar.addMenu(self.context.getText("menu", "file"))
		editMenu = menubar.addMenu(self.context.getText("menu", "edit"))
		viewMenu = menubar.addMenu(self.context.getText("menu", "view"))
		transformMenu = menubar.addMenu(self.context.getText("menu", "transform"))
		helpMenu = menubar.addMenu(self.context.getText("menu", "help"))
		fileActions = self.createFileActions()
		editActions = self.createEditActions()
		viewActions = self.createViewActions()
		transformActions = self.createTransformActions()
		helpActions = self.createHelpActions()
		for i in fileActions:
			if i == 0: fileMenu.addSeparator()
			else: fileMenu.addAction(i)
		for i in editActions:
			if i == 0: editMenu.addSeparator()
			else: editMenu.addAction(i)
		for i in viewActions:
			if i == 0: viewMenu.addSeparator()
			else: viewMenu.addAction(i)
		for i in helpActions:
			if i == 0: helpMenu.addSeparator()
			else: helpMenu.addAction(i)
		for i in transformActions:
			if i == 0: transformMenu.addSeparator()
			else: transformMenu.addAction(i)

		return menubar

	def createDockWidgets(self):
		
		# Palette widget
		self.palette = QtWidgets.QDockWidget(self.context.getText("dock_widgets", "palette"), self)
		self.palette.setAllowedAreas(Qt.RightDockWidgetArea)
		self.palette.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)

		paletteWidget = Palette(self.context, self.signals)

		self.palette.setWidget(paletteWidget)
		self.palette.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)

		self.addDockWidget(Qt.RightDockWidgetArea, self.palette)

		# Tool Properties widget
		self.toolProperties = ToolProperties(self.context.getText("dock_widgets", "tool_properties"), self.context, self.signals)
		self.addDockWidget(Qt.RightDockWidgetArea, self.toolProperties)
		self.toolProperties.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)

		# Preview
		self.preview = Preview(self.context.getText("dock_widgets", "preview"), self.context, self.signals, self)
		self.addDockWidget(Qt.RightDockWidgetArea, self.preview)

	def restoreFocus(self):

		print("Restoring Focus")
		self.ctrlPressed = False
		self.releaseMouse()
		self.releaseKeyboard()
		QtCore.QCoreApplication.instance().restoreOverrideCursor()

	def setCurrentTool(self, index):

		self.tools.actions()[0].setChecked(True)
		self.signals.updateTool.emit(0)

	def zoomIn(self):

		if self.context.currentImage().zoom < 25:
			self.context.currentImage().zoom += 1
			self.signals.zoom.emit()

	def zoomOut(self):

		if self.context.currentImage().zoom > 1:
			self.context.currentImage().zoom -= 1
			self.signals.zoom.emit()

	def newFile(self):

		d = NewFileDialog(self.context, self)

	def openFile(self):
		
		fileName = QtWidgets.QFileDialog.getOpenFileName(self,
					self.context.getText("dialog_open", "title"),
					"/home",
					self.context.getText("dialog_open", "images") + u" (*.bmp *.gif *.png *.xpm *.jpg);;" + self.context.getText("dialog_open", "all_files") + u" (*)")
		if fileName:
			self.context.loadImage(fileName)

	def saveFile(self):

		if self.context.currentImage().fileName == "":
			self.saveFileAs()
		else:	
			self.context.currentImage().save()

	def saveFileAs(self):

		d = QtWidgets.QFileDialog()
		fileName, filterName = d.getSaveFileName(self,
					self.context.getText("dialog_save", "title"), 
					"", 
					"*.bmp;;*.gif;;*.png;;*.xpm;;*.jpg")

		if fileName.split(".")[-1] in ["bmp", "gif", "png", "xpm", "jpg"]:
			self.context.currentImage().fileName = fileName
			self.signals.fileNameChanged.emit(self.context.getCurrentImagePos(), os.path.basename(str(fileName)))
		else:
			self.context.currentImage().fileName = fileName + filterName[1:]
			self.signals.fileNameChanged.emit(self.context.getCurrentImagePos(), os.path.basename(str(fileName + filterName[1:])))
		self.context.currentImage().save()

	def close(self):

		pass

	def undo(self):

		if self.context.currentImage().posHistory > 0:
			self.context.currentImage().posHistory -= 1
			self.context.currentImage().image = QtWidgets.QImage(self.context.currentImage().history[self.context.currentImage().posHistory])
			self.signals.updateCanvas.emit()
			self.signals.resizeCanvas.emit()

	def redo(self):

		if self.context.currentImage().posHistory < len(self.context.currentImage().history)-1:
			self.context.currentImage().posHistory += 1
			self.context.currentImage().image = QtWidgets.QImage(self.context.currentImage().history[self.context.currentImage().posHistory])
			self.signals.updateCanvas.emit()
			self.signals.resizeCanvas.emit()

	def selectAll(self):

		self.mainWidget.currentWidget().canvas.selectAll()

	def deselect(self):

		self.mainWidget.currentWidget().canvas.applySelection()

	def cut(self):

		self.signals.cutImage.emit()

	def copy(self):

		self.signals.copyImage.emit()

	def paste(self):

		clipboard = QtWidgets.QApplication.clipboard()
		if not clipboard.image().isNull():
			self.signals.pasteImage.emit()
			self.signals.updateCanvas.emit()

	def clear(self):

		self.signals.clearImage.emit()

	def showPreferences(self):

		d = Preferences(self.context, self.signals, self)

	def setPixelGrid(self):

		self.context.grid = not self.context.grid
		self.signals.updateCanvas.emit()
		self.context.setDefault("grid", "grid", self.context.grid)

	def setMatrixGrid(self):

		self.context.matrixGrid = not self.context.matrixGrid
		self.signals.updateCanvas.emit()
		self.context.setDefault("grid", "matrix_grid", self.context.matrixGrid)

	def flipHorizontally(self):

		pass

	def flipVertically(self):

		pass

	def rotate90CW(self):

		pass

	def rotate90CCW(self):

		pass

	def rotate180(self):

		pass

	def showResizeImageDialog(self):

		pass

	def showResizeCanvasDialog(self):

		pass

	def showHelp(self):

		pass

	def showAboutDialog(self):

		pass

	def showImagePosition(self):

		if self.imagePosLabel.isHidden():
			self.statusBar.insertWidget(0, self.imagePosLabel, 0)
			self.imagePosLabel.show()

	def hideImagePosition(self):

		self.statusBar.removeWidget(self.imagePosLabel)

	def setImagePosition(self, x, y):

		self.imagePosLabel.setText("  Pos: (" + str(x) + ", " + str(y) + ")")

	def keyPressEvent(self, event):

		super(MainWindow, self).keyPressEvent(event)

		if event.key() == Qt.Key_Control:
			print("Control Pressed")
			self.ctrlPressed = True
			QtCore.QCoreApplication.instance().setOverrideCursor(self.context.colorPickerCur)
			self.signals.ctrlPressed.emit()
			self.grabMouse()
			self.grabKeyboard()

		elif event.key() == Qt.Key_Plus:
			if self.context.currentTool == 1:
				self.context.setPencilSize(self.context.pencilSize+1)
			elif self.context.currentTool == 2:
				self.context.setEraserSize(self.context.eraserSize+1)

		elif event.key() == Qt.Key_Minus:
			if self.context.currentTool == 1:
				self.context.setPencilSize(self.context.pencilSize-1)
			elif self.context.currentTool == 2:
				self.context.setEraserSize(self.context.eraserSize-1)

		else:
			QtCore.QCoreApplication.instance().restoreOverrideCursor()
			self.releaseMouse()
			self.releaseKeyboard()

	def keyReleaseEvent(self, event):

		super(MainWindow, self).keyReleaseEvent(event)

		if event.key() == Qt.Key_Control:
			self.ctrlPressed = False
			QtCore.QCoreApplication.instance().restoreOverrideCursor()
			self.releaseMouse()
			self.releaseKeyboard()

	def mousePressEvent(self, event):

		super(MainWindow, self).mousePressEvent(event)

		if self.ctrlPressed:
			print("Picking Desktop Color")
			widget = QtCore.QCoreApplication.instance().desktop().screen()
			im = QtWidgets.QPixmap.grabWindow(widget.winId()).toImage() # Captura de pantalla
			c = QtWidgets.QColor(im.pixel(QtWidgets.QCursor.pos())) # Cogemos el color de la posición del cursor
			if event.button() == Qt.LeftButton:
				self.context.changePrimaryColor(c) # Cambiamos el color primario actual por el que hemos cogido
			elif event.button() == Qt.RightButton:
				self.context.changeSecondaryColor(c) # Cambiamos el color secundario actual por el que hemos cogido
			# im.save("desktop.png") # Guardar la captura de pantalla en un archivo
			# print "Getting color " + c.red(), c.green(), c.blue() + " from screen" # Comprueba qué color coge

	def mouseMoveEvent(self, event):

		super(MainWindow, self).mouseMoveEvent(event)

		# Lo mismo de antes pero para cuando el ratón se mueve
		if self.ctrlPressed:
			widget = QtCore.QCoreApplication.instance().desktop().screen()
			im = QtWidgets.QPixmap.grabWindow(widget.winId()).toImage() # Captura de pantalla
			c = QtWidgets.QColor(im.pixel(QtWidgets.QCursor.pos())) # Cogemos el color de la posición del cursor
			if event.buttons() == Qt.LeftButton:
				self.context.changePrimaryColor(c) # Cambiamos el color primario actual por el que hemos cogido
			elif event.buttons() == Qt.RightButton:
				self.context.changeSecondaryColor(c) # Cambiamos el color secundario actual por el que hemos cogido

	def wheelEvent(self, event):

		if self.ctrlPressed:
			if event.delta() > 0:
				self.zoomIn()
			else:
				self.zoomOut()

		super(MainWindow, self).wheelEvent(event)

	def closeEvent(self, event):

		l = []
		for i in range(len(self.context.images)):
			if self.context.images[i].modified: l.append(i)

		if len(l) > 0:
			# Mostrar diálogo
			reply = QtWidgets.QMessageBox.warning(self, self.context.getText("dialog_exit", "title"),
				self.context.getText("dialog_exit", "message"),
				QtWidgets.QMessageBox.SaveAll | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel,
				QtWidgets.QMessageBox.Cancel)
			if reply == QtWidgets.QMessageBox.Discard:
				event.accept()
			elif reply == QtWidgets.QMessageBox.Cancel:
				event.ignore()  
				return
			elif reply == QtWidgets.QMessageBox.SaveAll:
				for i in l:
					self.mainWidget.setCurrentIndex(i)
					self.context.setCurrentImagePos(i)
					self.saveFile()
				event.accept()
				return

			

		self.context.saveDefaults()

		super(MainWindow, self).closeEvent(event)
