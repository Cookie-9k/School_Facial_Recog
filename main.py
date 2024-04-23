from PyQt5 import QtWidgets
from library.core_function import Display_MainWindow
import sys

if __name__ == "__main__":
  app = QtWidgets.QApplication(sys.argv)
  window = Display_MainWindow()
  window.show()
  window.set_user_name("Unknown")
  sys.exit(app.exec_())