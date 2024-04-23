from PyQt5.QtWidgets import QDialog

from gui.aboutpageGui import Ui_Dialog

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
    
    def show_about(self):
        self.show()