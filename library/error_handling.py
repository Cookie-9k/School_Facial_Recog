from PyQt5.QtWidgets import QDialog

from gui.errordialog import Ui_Dialog

# Error Dialog
class ErrorDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.error_label = self.ui.label
        self.error_label.setText("No Errors")
    
    def show_error_message(self, error_message):
        self.error_label.setText(f"{error_message}")
        self.showNormal()