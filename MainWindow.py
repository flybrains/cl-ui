import os
import sys
import cv2
import math
import pickle
import time
import numpy as np
import importlib
import odorscape
import server
import csv
import datetime
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QBrush, QPen,QPolygonF

importlib.reload(server)
importlib.reload(odorscape)

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
		self.replayPB.clicked.connect(self.replay)
		self.runPB.clicked.connect(self.run)
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

	def run(self):
		self.configurator()
		server.run_fictrac_client(self.config_dict, self.gradient)

	def replay(self):
		self.gradient=None
		dialog = QFileDialog()
		dialog.setDefaultSuffix(".pkl")
		fname = dialog.getOpenFileName(self, 'Select Trial to Open', os.getcwd(), '(*.log)')[0]
		self.playback = []
		self.times = []
		with open(fname) as f:
			for idx, row in enumerate(f.read().split("\n")):
				if idx==0:
					pass
				else:
					try:
						time, toks = row.split(" -- ")[0], row.split(" -- ")[1]
						time = time.split("-")[1]
						self.times.append(time)
						toks = toks.split(', ')

						# posx, posy, mfc1, mfc2, mfc3
						self.playback.append([float(toks[1]),float(toks[2]),float(toks[4]),float(toks[5]),float(toks[6])])
					except IndexError:
						pass
		server.run_fictrac_client(self.config_dict, self.gradient, replay=[self.times, self.playback])

	def configurator(self):
		if self.constantFlowCheckbox.isChecked():
			self.gradientFlowCheckbox.setDisabled(True)
			self.gradientProfileSelectorPB.setDisabled(True)
			self.gradientProfileLabel.setDisabled(True)
			self.gradient=None
		if self.constantFlowCheckbox.isChecked()==False:
			self.gradientFlowCheckbox.setDisabled(False)
			self.gradientProfileSelectorPB.setDisabled(False)
			self.gradientProfileLabel.setDisabled(False)
			self.odor1ConcentrationLabel.setDisabled(False)
			self.odor1ConcentrationSpinbox.setDisabled(False)
		if self.gradientFlowCheckbox.isChecked():
			self.constantFlowCheckbox.setDisabled(True)
			self.odor1ConcentrationLabel.setDisabled(True)
			self.odor1ConcentrationSpinbox.setDisabled(True)
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

		self.RPI_HOST = self.rpiIPTextEdit.toPlainText()
		self.RPI_PORT = int(self.rpiCOMMTextEdit.toPlainText())
		self.LOCAL_HOST = self.localIPTextEdit.toPlainText()
		self.LOCAL_PORT = int(self.localCOMMTextEdit.toPlainText())
		self.CONSTANT_FLOW = bool(self.constantFlowCheckbox.isChecked())
		self.GRADIENT_FLOW = bool(self.gradientFlowCheckbox.isChecked())
		self.MAX_FLOW_RATE = int(self.flowRateSpinbox.value())
		if self.conditionalLEDStimulationRadioButton.isChecked():
			self.LED_ACTIVATION_MODE = "conditional"
		if self.fixedLEDStimulationRadioButton.isChecked():
			self.LED_ACTIVATION_MODE = "temporal"
		if self.noneLEDStimulationRadioButton.isChecked():
			self.LED_ACTIVATION_MODE = None
		if self.redLEDRadioButton.isChecked():
			self.LED_COLOR = 'red'
		if self.greenLEDRadioButton.isChecked():
			self.LED_COLOR = 'green'
		self.LED_INTENSITY = int(self.ledIntensitySpinbox.value())
		self.LED_DURATION = float(self.pulseDurationSpinbox.value())
		self.LED_INITIAL_DELAY = float(self.initialDelaySpinbox.value())
		self.LED_PERIOD = float(self.pulsePeriodSpinbox.value())
		self.LED_POST_ACT_LOCK = float(self.postPulseLockSpinbox.value())
		self.LED_CONDITION_THRESHOLD = float(self.conditionThresholdSpinbox.value())
		self.SLIDING_WINDOW_LENGTH = int(self.slidingWindowSpinbox.value())
		self.PERCENT_ODOR1 = int(self.odor1ConcentrationSpinbox.value())
		self.config_dict={"RPI_HOST":self.RPI_HOST,
					  	"RPI_PORT":self.RPI_PORT,
						"LOCAL_HOST":self.LOCAL_HOST,
						"LOCAL_PORT":self.LOCAL_PORT,
						"CONSTANT_FLOW":self.CONSTANT_FLOW,
						"PERCENT_CONSTANT_ODOR1":self.PERCENT_ODOR1,
						"GRADIENT_FLOW":self.GRADIENT_FLOW,
						"MAX_FLOW_RATE":self.MAX_FLOW_RATE,
						"LED_ACTIVATION_MODE":self.LED_ACTIVATION_MODE,
						"LED_COLOR":self.LED_COLOR,
						"LED_INTENSITY":self.LED_INTENSITY,
						"LED_DURATION":self.LED_DURATION,
						"LED_INITIAL_DELAY":self.LED_INITIAL_DELAY,
						"LED_PERIOD":self.LED_PERIOD,
						"LED_POST_ACT_LOCK":self.LED_POST_ACT_LOCK,
						"LED_CONDITION_THRESHOLD":self.LED_CONDITION_THRESHOLD,
						"SLIDING_WINDOW_LENGTH":self.SLIDING_WINDOW_LENGTH}

	# def connectFictrac(self):
	# 	#Bash command
	#
	# def connectRPi(self):
	# 	# Bash Command

	def loadGradient(self):
		dialog = QFileDialog()
		dialog.setDefaultSuffix(".pkl")
		fname = dialog.getOpenFileName(self, 'Select Gradient to Open', os.getcwd(), '(*.pkl)')[0]
		pickle_in = open(fname, "rb")
		temp = pickle.load(pickle_in)
		self.canvas = odorscape.Canvas(temp.w, temp.h, module=True)
		self.canvas.airchannel = temp.airchannel
		self.canvas.channel1 = temp.channel1
		self.canvas.channel2 = temp.channel2
		self.gradient = self.canvas.build_canvas()
		self.gradientProfileLabel.setText(fname)
		self.loadGradientLabel.setStyleSheet("background-color : rgb(0,255,0); color : green;")

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = ClosedLoop()
	window.show()
	sys.exit(app.exec_())
