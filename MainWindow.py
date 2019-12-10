import os
import sys
import cv2
import math
import pickle
import time
import numpy as np
from odorscape import Canvas
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QBrush, QPen,QPolygonF

cwd = os.getcwd()
mainWindowCreatorFile = cwd+"/ClosedLoop2.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(mainWindowCreatorFile)



class ClosedLoop(QtWidgets.QMainWindow, Ui_MainWindow):
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)
		self.setupUi(self)
		self.setWindowTitle('Closed Loop')
		self.setFixedSize(self.size())

		# self.connectRPiPB.clicked.connect(self.connectRPi)
		# self.connectFictracPB.clicked.connect(self.connectFictrac)
		self.loadGradientPB.clicked.connect(self.loadGradient)
		self.gradientProfileSelectorPB.clicked.connect(self.loadGradient)
		# self.edgeRulesPB.clicked.connect(self.defineEdgeRules)
		# self.replayPB.clicked.connect(self.replay)
		# self.runPB.clicked.connect(self.run)
		# self.stopPB.clicked.connect(self.stop)

		self.conditionalLEDStimulationRadioButton.clicked.connect(self.configurator)
		self.fixedLEDStimulationRadioButton.clicked.connect(self.configurator)
		self.noneLEDStimulationRadioButton.clicked.connect(self.configurator)
		self.uwTrackingConditionRadioButton.clicked.connect(self.configurator)
		self.noneConditionRadioButton.clicked.connect(self.configurator)
		self.redLEDRadioButton.clicked.connect(self.configurator)
		self.greenLEDRadioButton.clicked.connect(self.configurator)
		self.gradientFlowCheckbox.clicked.connect(self.configurator)
		self.constantFlowCheckbox.clicked.connect(self.configurator)
		self.flowRateSpinbox.valueChanged.connect(self.configurator)
		self.noneLEDStimulationRadioButton.setChecked(True)
		self.noneConditionRadioButton.setChecked(True)
		self.redLEDRadioButton.setChecked(True)
		self.rpiIPTextEdit.setText("000.000.000.000")
		self.rpiCOMMTextEdit.setText("00000")
		self.localIPTextEdit.setText("000.000.000.000")
		self.localCOMMTextEdit.setText("00000")
		self.configurator()

	def replay(self):
		dialog = QFileDialog()
		dialog.setDefaultSuffix(".pkl")
		fname = dialog.getOpenFileName(self, 'Select Trial to Open', os.getcwd(), '(*.dat)')[0]

	def configurator(self):
		if self.constantFlowCheckbox.isChecked():
			self.gradientFlowCheckbox.setDisabled(True)
			self.gradientProfileSelectorPB.setDisabled(True)
			self.gradientProfileLabel.setDisabled(True)
		if self.constantFlowCheckbox.isChecked()==False:
			self.gradientFlowCheckbox.setDisabled(False)
			self.gradientProfileSelectorPB.setDisabled(False)
			self.gradientProfileLabel.setDisabled(False)
		if self.gradientFlowCheckbox.isChecked():
			self.constantFlowCheckbox.setDisabled(True)
		if self.gradientFlowCheckbox.isChecked()==False:
			self.constantFlowCheckbox.setDisabled(False)

		if self.conditionalLEDStimulationRadioButton.isChecked():
			self.ledIntensitySpinbox.setDisabled(False)
			self.pulseDurationSpinbox.setDisabled(False)
			self.initialDelaySpinbox.setDisabled(False)
			self.pulsePeriodSpinbox.setDisabled(True)
			self.postPulseLockSpinbox.setDisabled(False)
			self.conditionThresholdSpinbox.setDisabled(False)
			self.slidingWindowSpinbox.setDisabled(False)

			if self.noneConditionRadioButton.isChecked():
				self.postPulseLockSpinbox.setDisabled(True)
				self.conditionThresholdSpinbox.setDisabled(True)
				self.slidingWindowSpinbox.setDisabled(True)

		if self.fixedLEDStimulationRadioButton.isChecked():
			self.ledIntensitySpinbox.setDisabled(False)
			self.pulseDurationSpinbox.setDisabled(False)
			self.initialDelaySpinbox.setDisabled(False)
			self.pulsePeriodSpinbox.setDisabled(False)
			self.postPulseLockSpinbox.setDisabled(True)
			self.conditionThresholdSpinbox.setDisabled(True)
			self.slidingWindowSpinbox.setDisabled(True)
			self.greenLEDRadioButton.setDisabled(False)
			self.redLEDRadioButton.setDisabled(False)

		if self.noneLEDStimulationRadioButton.isChecked():
			self.ledIntensitySpinbox.setDisabled(True)
			self.pulseDurationSpinbox.setDisabled(True)
			self.initialDelaySpinbox.setDisabled(True)
			self.pulsePeriodSpinbox.setDisabled(True)
			self.postPulseLockSpinbox.setDisabled(True)
			self.conditionThresholdSpinbox.setDisabled(True)
			self.slidingWindowSpinbox.setDisabled(True)
			self.greenLEDRadioButton.setDisabled(True)
			self.redLEDRadioButton.setDisabled(True)

	def connectFictrac(self):
		#Bash command

	def connectRPi(self):
		# Bash Command


	def loadGradient(self):
		dialog = QFileDialog()
		dialog.setDefaultSuffix(".pkl")
		fname = dialog.getOpenFileName(self, 'Select Gradient to Open', os.getcwd(), '(*.pkl)')[0]
		pickle_in = open(fname, "rb")
		temp = pickle.load(pickle_in)
		self.canvas = Canvas(temp.w, temp.h, module=True)
		self.canvas.airchannel = temp.airchannel
		self.canvas.channel1 = temp.channel1
		self.canvas.channel2 = temp.channel2
		self.gradient = self.canvas.build_canvas()
		self.gradientProfileLabel = fname
		self.loadGradientLabel.setStyleSheet("background-color : rgb(0,255,0); color : green;")

		print(self.gradient.shape)





if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = ClosedLoop()
	window.show()
	sys.exit(app.exec_())





# class ErrorMsg(QtWidgets.QMessageBox):
# 	def __init__(self, msg, parent=None):
# 		super(ErrorMsg, self).__init__(parent)
# 		self.setIcon(QtWidgets.QMessageBox.Critical)
# 		self.setText(msg)
# 		self.setWindowTitle('Error')
#
# class CanvasSizeConfigWindow(QtWidgets.QDialog):
# 	got_values = QtCore.pyqtSignal(int)
# 	def __init__(self, parent=None):
# 		super(CanvasSizeConfigWindow, self).__init__(parent)
# 		self.l1 = QtWidgets.QLabel('Canvas Height (mm)')
# 		self.l2 = QtWidgets.QLabel('Canvas Width (mm)')
# 		self.pb = QtWidgets.QPushButton()
# 		self.l1Edit = QtWidgets.QSpinBox()
# 		self.l1Edit.setMaximum(10000000)
# 		self.l1Edit.setValue(1000)
# 		self.l2Edit = QtWidgets.QSpinBox()
# 		self.l2Edit.setMaximum(10000000)
# 		self.l2Edit.setValue(1000)
# 		self.pb.setText("Set Canvas Size")
# 		self.grid = QtWidgets.QGridLayout()
# 		self.grid.setSpacing(5)
# 		self.grid.addWidget(self.l1, 1, 0)
# 		self.grid.addWidget(self.l1Edit, 1, 1)
# 		self.grid.addWidget(self.l2, 2, 0)
# 		self.grid.addWidget(self.l2Edit, 2, 1)
# 		self.grid.addWidget(self.pb, 4, 1)
# 		self.setLayout(self.grid)
# 		self.setGeometry(400, 400, 200, 100 )
# 		self.setWindowTitle('Canvas Size Configuration')
# 		#self.show()
# 		self.pb.clicked.connect(self.store_values)
# 		return None
#
# 	def store_values(self):
# 		self.h = int(self.l1Edit.value())
# 		self.w = int(self.l2Edit.value())
# 		self.got_values.emit(1)
# 		self.close()
# 		return None
#
# class RectangularSourceConfigWindow(QtWidgets.QDialog):
# 	got_values = QtCore.pyqtSignal(int)
# 	def __init__(self, canvas,parent=None):
# 		super(RectangularSourceConfigWindow, self).__init__(parent)
# 		self.canvas = canvas
# 		self.l1 = QtWidgets.QLabel('Origin X (mm)')
# 		self.l1Edit = QtWidgets.QSpinBox()
# 		self.l1Edit.setRange(-int(canvas.w/2),int(canvas.w/2))
#
# 		self.l2 = QtWidgets.QLabel('Origin Y (mm)')
# 		self.l2Edit = QtWidgets.QSpinBox()
# 		self.l2Edit.setMaximum(canvas.h)
# 		self.l2Edit.setRange(-int(canvas.h/2),int(canvas.h/2))
#
# 		self.l3 = QtWidgets.QLabel('Width (mm)')
# 		self.l3Edit = QtWidgets.QSpinBox()
# 		self.l3Edit.setRange(0,int(canvas.w))
#
# 		self.l4 = QtWidgets.QLabel('Height (mm)')
# 		self.l4Edit = QtWidgets.QSpinBox()
# 		self.l4Edit.setRange(0,int(canvas.h))
#
# 		self.l5 = QtWidgets.QLabel('Max Value')
# 		self.l5Edit = QtWidgets.QSpinBox()
# 		self.l5Edit.setMaximum(255)
# 		self.l5Edit.setMinimum(0)
#
# 		self.l6 = QtWidgets.QLabel('Min Value')
# 		self.l6Edit = QtWidgets.QSpinBox()
# 		self.l6Edit.setMaximum(255)
# 		self.l6Edit.setMinimum(0)
#
# 		self.l7 = QtWidgets.QLabel('Max at: ')
# 		self.comboBox7 = QtWidgets.QComboBox(self)
# 		self.comboBox7.addItem("Top")
# 		self.comboBox7.addItem("Bottom")
# 		self.comboBox7.addItem("Left")
# 		self.comboBox7.addItem("Right")
#
# 		self.l8 = QtWidgets.QLabel('Odor Channel')
# 		self.comboBox8 = QtWidgets.QComboBox(self)
# 		self.comboBox8.addItem("1")
# 		self.comboBox8.addItem("2")
# 		self.l9 =  QtWidgets.QLabel('')
# 		self.pb = QtWidgets.QPushButton()
#
# 		self.pb.setText("Add Source")
# 		self.grid = QtWidgets.QGridLayout()
# 		self.grid.setSpacing(1)
# 		self.grid.addWidget(self.l1, 1, 0)
# 		self.grid.addWidget(self.l1Edit, 1, 1)
# 		self.grid.addWidget(self.l2, 2, 0)
# 		self.grid.addWidget(self.l2Edit, 2, 1)
# 		self.grid.addWidget(self.l3, 3, 0)
# 		self.grid.addWidget(self.l3Edit, 3, 1)
# 		self.grid.addWidget(self.l4, 4, 0)
# 		self.grid.addWidget(self.l4Edit, 4, 1)
# 		self.grid.addWidget(self.l5, 5, 0)
# 		self.grid.addWidget(self.l5Edit, 5, 1)
# 		self.grid.addWidget(self.l6, 6, 0)
# 		self.grid.addWidget(self.l6Edit, 6, 1)
# 		self.grid.addWidget(self.l7, 7, 0)
# 		self.grid.addWidget(self.comboBox7, 7, 1)
# 		self.grid.addWidget(self.l8, 8, 0)
# 		self.grid.addWidget(self.comboBox8, 8, 1)
# 		self.grid.addWidget(self.pb, 9, 0)
# 		self.grid.addWidget(self.l9, 9, 1)
# 		self.setLayout(self.grid)
# 		self.setGeometry(400, 400, 300, 500)
# 		self.setWindowTitle("Rectangular Source Configuration")
# 		self.pb.clicked.connect(self.store_values)
#
# 		self.show()
# 	# 	self.setMouseTracking(True)
# 	#
# 	# def mouseMoveEvent(self, event):
# 	# 	if event.x() <=988 and event.y() <=758 and event.x() >=288 and event.y() >=58 and self.initialized:
# 	# 		x = event.x() - 289
# 	# 		y = event.y() - 59
# 	# 		c = self.imageRef.pixel(x,y)
# 	# 		colors = QtGui.QColor(c).getRgbF()
# 	#
# 	#
# 	# 		self.airValLabel.setText("({})".format(int(colors[2]*255)))
# 	# 		self.odor1ValLabel.setText("({})".format(int(colors[1]*255)))
# 	# 		self.odor2ValLabel.setText("({})".format(int(colors[0]*255)))
#
# 	def store_values(self):
# 		self.l9.setText('  Processing...')
# 		self.l9.repaint()
# 		self.x = int(self.l1Edit.value()+(self.canvas.w/2))
# 		self.y = -int(self.l2Edit.value())+int(self.canvas.h/2)
# 		self.w = int(self.l3Edit.value())
# 		self.h = int(self.l4Edit.value())
# 		self.max = int(self.l5Edit.value())
# 		self.min = int(self.l6Edit.value())
# 		self.maxat = str(self.comboBox7.currentText())
# 		self.channel = str(self.comboBox8.currentText())
# 		self.got_values.emit(1)
# 		self.close()
# 		return None
#
# class Odorscape(QtWidgets.QMainWindow, Ui_MainWindow):
# 	def __init__(self):
# 		QtWidgets.QMainWindow.__init__(self)
# 		Ui_MainWindow.__init__(self)
# 		self.setupUi(self)
# 		self.setWindowTitle('Odorscape')
# 		self.setFixedSize(self.size())
# 		self.canvas = Canvas()
# 		self.actionNewCanvas.triggered.connect(self.initializeCanvas)
# 		self.actionOpenCanvas.triggered.connect(self.loadCanvas)
# 		self.actionSaveCanvas.triggered.connect(self.saveCanvas)
# 		self.actionClearCanvas.triggered.connect(self.clearCanvas)
# 		self.canvasconfigwindow = CanvasSizeConfigWindow()
# 		self.canvasconfigwindow.got_values.connect(self.displayCanvas)
# 		self.rectangularGradientButton.clicked.connect(self.initializeRectBuilder)
# 		self.circularGradientButton.clicked.connect(self.initializeCircleBuilder)
# 		self.rollbackPushButton.clicked.connect(self.rollbackCanvas)
# 		self.rectangularGradientButton.setDisabled(True)
# 		self.circularGradientButton.setDisabled(True)
# 		self.rollbackPushButton.setDisabled(True)
# 		self.initialized=False
# 		self.setMouseTracking(True)
#
# 	def mouseMoveEvent(self, event):
# 		if event.x() <=1010 and event.y() <=762 and event.x() >=310 and event.y() >=62 and self.initialized:
# 			x = event.x() - 311
# 			y = event.y() - 63
# 			c = self.imageRef.pixel(x,y)
# 			colors = QtGui.QColor(c).getRgbF()
#
# 			self.airValLabel.setText("({})".format(int(colors[2]*255)))
# 			self.odor1ValLabel.setText("({})".format(int(colors[1]*255)))
# 			self.odor2ValLabel.setText("({})".format(int(colors[0]*255)))
#
# 	def initializeCanvasHistory(self):
# 		if 'canvas_data' in os.listdir(os.getcwd()):
# 			for filename in os.listdir(os.path.join(os.getcwd(),'canvas_data')):
# 				os.remove(os.path.join(os.getcwd(), 'canvas_data', filename))
# 		else:
# 			os.mkdir(os.path.join(os.getcwd(), 'canvas_data'))
#
# 		return None
#
# 	def initializeCanvas(self):
# 		self.initializeCanvasHistory()
# 		self.rectangularGradientButton.setDisabled(False)
# 		self.circularGradientButton.setDisabled(False)
# 		self.canvasconfigwindow.show()
# 		self.initialized = True
# 		return None
#
# 	def clearCanvas(self):
# 		self.initializeCanvasHistory()
# 		self.canvas = Canvas(self.canvasconfigwindow.w, self.canvasconfigwindow.h)
# 		self.canvasImage = self.canvas.build_canvas()
# 		self.setCanvas(self.canvasImage)
# 		return None
#
# 	def saveCanvas(self):
# 		self.canvasSavePath = QFileDialog.getSaveFileName(self, 'Select Save Directory', os.getcwd())
# 		self.commonName = self.canvasSavePath[0]
# 		self.canvasSavePath = self.canvasSavePath[0]+".pkl"
#
# 		if self.initialized==False:
# 			msg = 'Must initialize a canvas before saving'
# 			self.error = ErrorMsg(msg)
# 			self.error.show()
# 		else:
# 			pickle_out = open(self.canvasSavePath,"wb")
# 			pickle.dump(self.canvas, pickle_out)
# 			pickle_out.close()
# 			self.commonNameLabel.setText(self.commonName)
# 		return None
#
# 	def loadCanvas(self):
# 		fname = QFileDialog.getOpenFileName(self, 'Select Program to Open', os.getcwd())
# 		self.openCanvasPath = str(fname[0])
# 		pickle_in = open(self.openCanvasPath, "rb")
# 		temp = pickle.load(pickle_in)
# 		self.canvas = Canvas(temp.w, temp.h)
# 		self.canvas.airchannel = temp.airchannel
# 		self.canvas.channel1 = temp.channel1
# 		self.canvas.channel2 = temp.channel2
# 		self.canvasImage = self.canvas.build_canvas()
# 		self.setCanvas(self.canvasImage)
# 		self.initializeCanvasHistory()
# 		self.rectangularGradientButton.setDisabled(False)
# 		self.circularGradientButton.setDisabled(False)
# 		self.initialized = True
# 		self.commonName = self.openCanvasPath[:-4]
# 		self.commonNameLabel.setText(self.commonName)
#
# 		return None
#
# 	@pyqtSlot(QImage)
# 	def setCanvas(self, image):
# 		image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
# 		image = image.copy()
# 		self.qimage = QImage(image, image.shape[0], image.shape[1], QImage.Format_RGB888)
# 		self.qimage = self.qimage.scaled(700,700)
# 		pixmap = QPixmap(self.qimage)
# 		#pixmap = pixmap.scaled(700,700)
# 		self.imageRef = self.qimage.scaled(700,700)
# 		self.canvasLabel.setPixmap(pixmap)
# 		self.canvasLabel.show()
#
# 	def displayCanvas(self, init=True):
# 		if init:
# 			self.canvas = Canvas(self.canvasconfigwindow.w, self.canvasconfigwindow.h)
# 		self.canvasImage = self.canvas.build_canvas()
# 		self.leftCanvasLabel.setText("({}, {})".format(str(round((-1*(self.canvas.w/2)/1000), 2)), 0))
# 		self.topCanvasLabel.setText("({}, {})".format(0, str(round((1*(self.canvas.h/2)/1000), 2))))
# 		self.rightCanvasLabel.setText("  ({}, {})".format(str(round(((self.canvas.w/2)/1000), 2)), 0))
# 		self.bottomCanvasLabel.setText("({}, {})".format(0, str(round(((-1*self.canvas.h/2)/1000), 2))))
# 		self.setCanvas(self.canvasImage)
# 		self.setCanvas(self.canvasImage)
# 		self.displayAnnotation()
#
# 	def displayAnnotation(self):
# 		overlay = QImage(os.getcwd()+"/assets/arrow.png")
# 		overlay = overlay.scaled(50,50)
# 		painter = QPainter()
# 		painter.begin(self.qimage)
# 		painter.drawImage(325, 325, overlay)
# 		painter.end()
# 		self.canvasLabel.setPixmap(QPixmap.fromImage(self.qimage))
# 		self.canvasLabel.show()
#
# 	def rollbackCanvas(self):
# 		self.canvasImage = self.canvas.rollback_canvas()
# 		self.setCanvas(self.canvasImage)
#
# 	def initializeRectBuilder(self, show=False):
# 		self.rectconfigwindow = RectangularSourceConfigWindow(self.canvas)
# 		self.rectconfigwindow.got_values.connect(self.addRectangularGradient)
#
# 	def initializeCircleBuilder(self, show=False):
# 		self.circleconfigwindow = CircularSourceConfigWindow(self.canvas)
# 		self.circleconfigwindow.got_values.connect(self.addCircularGradient)
#
# 	def addRectangularGradient(self):
#
# 		self.rollbackPushButton.setDisabled(False)
# 		x = self.rectconfigwindow.x
# 		y = self.rectconfigwindow.y
# 		h = self.rectconfigwindow.h
# 		w = self.rectconfigwindow.w
# 		max = self.rectconfigwindow.max
# 		min = self.rectconfigwindow.min
# 		channel = self.rectconfigwindow.channel
# 		maxat = self.rectconfigwindow.maxat
#
# 		self.canvas.add_square_gradient(x,y,w,h,max, min, channel, maxat=maxat)
# 		self.canvas.check_and_correct_overlap()
# 		self.displayCanvas(init=False)
# 		return None
#
# 	def addCircularGradient(self):
# 		self.rollbackPushButton.setDisabled(False)
# 		x = self.circleconfigwindow.x
# 		y = self.circleconfigwindow.y
# 		r = self.circleconfigwindow.r
# 		max = self.circleconfigwindow.max
# 		min = self.circleconfigwindow.min
# 		channel = self.circleconfigwindow.channel
#
# 		self.canvas.add_circular_gradient(x,y,r,max, min, channel)
# 		self.canvas.check_and_correct_overlap()
# 		self.displayCanvas(init=False)
# 		return None
#
# class CircularSourceConfigWindow(QtWidgets.QDialog):
# 	got_values = QtCore.pyqtSignal(int)
# 	def __init__(self, canvas,parent=None):
# 		super(CircularSourceConfigWindow, self).__init__(parent)
# 		self.canvas = canvas
# 		self.l1 = QtWidgets.QLabel('Origin X (mm)')
# 		self.l1Edit = QtWidgets.QSpinBox()
# 		self.l1Edit.setRange(-int(canvas.w),int(canvas.w))
#
# 		self.l2 = QtWidgets.QLabel('Origin Y (mm)')
# 		self.l2Edit = QtWidgets.QSpinBox()
# 		self.l2Edit.setRange(-int(canvas.h),int(canvas.h))
#
# 		self.l3 = QtWidgets.QLabel('Radius (mm)')
# 		self.l3Edit = QtWidgets.QSpinBox()
# 		self.l3Edit.setMaximum(100000)
# 		self.l3Edit.setMinimum(0)
#
# 		self.l4 = QtWidgets.QLabel('Max Value')
# 		self.l4Edit = QtWidgets.QSpinBox()
# 		self.l4Edit.setMaximum(255)
# 		self.l4Edit.setMinimum(0)
#
# 		self.l5 = QtWidgets.QLabel('Min Value')
# 		self.l5Edit = QtWidgets.QSpinBox()
# 		self.l5Edit.setMaximum(255)
# 		self.l5Edit.setMinimum(0)
#
# 		self.l6 = QtWidgets.QLabel('Odor Channel')
# 		self.comboBox6 = QtWidgets.QComboBox(self)
# 		self.comboBox6.addItem("1")
# 		self.comboBox6.addItem("2")
# 		self.l7 =  QtWidgets.QLabel('')
#
# 		self.pb = QtWidgets.QPushButton()
#
# 		self.pb.setText("Add Source")
# 		self.grid = QtWidgets.QGridLayout()
# 		self.grid.setSpacing(1)
# 		self.grid.addWidget(self.l1, 1, 0)
# 		self.grid.addWidget(self.l1Edit, 1, 1)
# 		self.grid.addWidget(self.l2, 2, 0)
# 		self.grid.addWidget(self.l2Edit, 2, 1)
# 		self.grid.addWidget(self.l3, 3, 0)
# 		self.grid.addWidget(self.l3Edit, 3, 1)
# 		self.grid.addWidget(self.l4, 4, 0)
# 		self.grid.addWidget(self.l4Edit, 4, 1)
# 		self.grid.addWidget(self.l5, 5, 0)
# 		self.grid.addWidget(self.l5Edit, 5, 1)
# 		self.grid.addWidget(self.l6, 7, 0)
# 		self.grid.addWidget(self.comboBox6, 7, 1)
# 		self.grid.addWidget(self.pb, 9, 0)
# 		self.grid.addWidget(self.l7, 9, 1)
# 		self.setLayout(self.grid)
# 		self.setGeometry(400, 400, 300, 500)
# 		self.setWindowTitle("Circular Source Configuration")
# 		self.pb.clicked.connect(self.store_values)
# 		self.show()
#
#
# 	def store_values(self):
# 		self.l7.setText('  Processing...')
# 		self.l7.repaint()
# 		self.x = int(self.l1Edit.value()+(self.canvas.w/2))
# 		self.y = -int(self.l2Edit.value())+int(self.canvas.h/2)
# 		self.r = int(self.l3Edit.value())
# 		self.max = int(self.l4Edit.value())
# 		self.min = int(self.l5Edit.value())
# 		self.channel = str(self.comboBox6.currentText())
# 		self.got_values.emit(1)
# 		self.close()
# 		return None
