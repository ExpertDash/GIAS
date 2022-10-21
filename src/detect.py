import win32gui
from typing import Iterator, List
from pyscreeze import Box
from pyautogui import *

defaultConfidence = 0.9

def isCursorVisible() -> bool:
	cursor = win32gui.GetCursorInfo()
	flags = cursor[1]

	return bool(flags & 0x00000001)

def captureBox(box: Box, name: str = None, pad: int = 50):
	left, top, width, height = box.left, box.top, box.width, box.height

	if not name:
		name = f"box(pos={left} {top} size={width} {height})"

	screenshot(
		f"output/{name}.png",
		region=(left - pad/2, top - pad/2, width + pad, height + pad)
	)

def findFeatures(*names: List[str], confidence: float = defaultConfidence, region: Box = None) -> Iterator[Box]:
	for name in names:
		box: Box = locateOnScreen(
			f"resources/{name}.png",
			confidence=confidence,
			region=region,
			grayscale=True
		)

		if box is not None:
			yield box

def findFeature(name: str, confidence: float = defaultConfidence, region: Box = None) -> Box:
	return next(findFeatures(name, confidence=confidence, region=region), None)