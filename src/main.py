from overlay import Overlay
from PyQt5.QtWidgets import QApplication

app = QApplication([])

overlay = Overlay()
overlay.show()

app.exec()

# w, h = size()
# screenshot("output/sc.png", (int(w*0.25), int(h*0.9), int(w*0.5), int(h*0.1)) # speech indicator