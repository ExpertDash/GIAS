from __future__ import annotations

import time
import pyautogui as autogui
from typing import NamedTuple
from detect import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Overlay(QMainWindow):
	timer: QTimer
	mode: Mode
	elements: List[Element]

	def __init__(self):
		super().__init__()

		self.setAttribute(Qt.WA_TranslucentBackground)

		self.setWindowFlags(
			Qt.WindowStaysOnTopHint
			| Qt.FramelessWindowHint
			| Qt.X11BypassWindowManagerHint
		)

		self.setGeometry(QStyle.alignedRect(
			Qt.LeftToRight, Qt.AlignTop | Qt.AlignLeft,
			QSize(*autogui.size()),
			qApp.desktop().availableGeometry()
		))

		self.mode = (0, 0, 1)
		self.elements = []

		self.graphicsTimer = QTimer(self, timeout=self.update, interval=33)
		self.logicTimer = QTimer(self, timeout=self.updateLogic, interval=500)

		self.graphicsTimer.start()
		self.logicTimer.start()

	@property
	def logicInterval(self) -> float:
		return self.logicTimer.interval / 1000

	@logicInterval.setter
	def logicInterval(self, value: float):
		self.logicTimer.setInterval(int(value * 1000))

	def updateLogic(self):
		self.mode = (0, 0, 1)

		# Not in world
		if not isCursorVisible():
			self.clearElements()
			return

		self.mode = (1, 0, 1)

		# Not in menu or holding alt in world
		w, h = autogui.size()
		if any(findFeatures("close", "return", "characters", "exit", confidence=0.8, region=(0, 0, w, int(h*0.1)))):
			self.clearElements()
			return

		self.mode = (1, 0, 0)

		# Get dialogue options
		optionBoxes = [*locateAllOnScreen(
			"resources/dialogue.png",
			confidence=0.85,
			region=(int(w/2), int(h*0.3), int(w/2), int(h*0.7)),
			grayscale=True
		)]

		# Check if any exist
		if optionBoxes:
			self.mode = (1, 1, 0)

			# Sort boxes from bottom to top
			optionBoxes.sort(key=lambda b: b.top, reverse=True)
			firstBox = optionBoxes[0]

			self.clearElements()

			for box in optionBoxes:
				self.addElement(Element(box, color=Element.Color(255, 255, 0)))

			def select():
				# Log
				print(f"Selecting dialogue box: {box}")

				# Click on the bottom option
				mouseX, mouseY = position()
				
				click(x=firstBox.left + firstBox.width/2, y=firstBox.top + firstBox.height/2)
				moveTo(mouseX, mouseY)

				self.clearElements()
				self.logicTimer.start()

			self.logicTimer.stop()
			QTimer.singleShot(1000, select)
		else:
			feature = findFeature("toggle_speech_auto", confidence=0.75, region=(0, 0, int(w*0.2), int(h*0.2)))

			self.clearElements()

			if not feature:
				return

			self.mode = (0, 1, 1)

			self.addElement(Element(feature, color=Element.Color(0, 255, 255)))

			# Log
			print(f"Attempting to skip speech...")

			# mouseX, mouseY = position()
			# click(x=w/2, y=h/2)
			# moveTo(mouseX, mouseY)

	def closeEvent(self, _: QCloseEvent):
		self.graphicsTimer.stop()
		self.logicTimer.stop()

	def paintEvent(self, _: QPaintEvent):
		painter = QPainter(self)

		a, s = 175, 50
		b = 255 - a
		c = time.time() * s % (b * 2)
		t = int(a + (c if c <= b else (b * 2) - c))

		r, g, b = self.mode

		pen = QPen()
		pen.setWidth(5)
		pen.setColor(QColor(r * t, g * t, b * t))
		painter.setPen(pen)
		
		font = painter.font()
		font.setPointSize(12)
		painter.setFont(font)

		painter.drawText(10, 20, "gias")

		for element in self.elements:
			r, g, b, a = element.color
			pen.setColor(QColor(r, g, b, a))

			pad = 20
			x, y, w, h = element.box
			painter.setPen(pen)
			painter.drawRect(QRect(x - pad/2, y - pad/2, w + pad, h + pad))

	def addElement(self, element: Element):
		self.elements.append(element)

	def clearElements(self):
		self.elements.clear()

class Mode(NamedTuple):
	r: float
	g: float
	b: float

class Element:
	def __init__(self, box: Element.Box, name: str = None, color: Element.Color = None):
		self.box = box
		self.name = name
		self.color = color or Element.Color()

	class Box(NamedTuple):
		x: int
		y: int
		width: int
		height: int

	class Color(NamedTuple):
		r: int = 0
		g: int = 0
		b: int = 0
		a: int = 255