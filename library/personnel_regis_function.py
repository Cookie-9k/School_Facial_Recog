from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

from gui.regisGui_staff import Ui_Dialog
import library.data_handling as dthd
import library.error_handling as errh

import os
import cv2
import openpyxl as excel

# Personnel GUI Processes
class PersonnelRegisterDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.error_dialog = errh.ErrorDialog()

        # Variables pointing to all the GUI objects required
        self.camera = dthd.ProgramState.capture

        self.image_label = self.ui.cameraSurface
        self.firstname = self.ui.input_frstnme
        self.middlename = self.ui.input_mi
        self.lastname = self.ui.input_lstnme
        self.department = self.ui.comboBox
        self.dialogbuttons = self.ui.buttonBox

        # Button Actions
        self.dialogbuttons.accepted.connect(lambda: self.save_user_data())
        self.dialogbuttons.rejected.connect(self.close)

        # Prerequisites of the program
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(30)

    # Updates cameraSurface GUI Object accordingly
    def update_image(self):
        if dthd.ProgramState.registeringpersonnel == True:
            try:
                # Capture a frame from the camera
                ret, frame = self.camera.read()

                # Convert the frame to a QImage
                height, width, channels = frame.shape
                bytes_per_line = channels * width
                q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)

                # Display the QImage in the QLabel
                pixmap = QPixmap.fromImage(q_image)
                self.image_label.setPixmap(pixmap)
            except:
                dthd.ProgramState.registeringpersonnel = False
                print("Error Displaying Camera")

    # Takes a single photo
    def take_photo(self):
        raw_file_name = f"{self.department.currentText().lower()}_{self.firstname.text().lower()} {self.lastname.text().lower()}.png"
        file_name = raw_file_name.replace(" ","_")
        if len(file_name) > 6:
            ret, frame = self.camera.read()
            program_dir = os.getcwd()
            object_path = os.path.join(program_dir, f"image_bank/{file_name}")
            cv2.imwrite(object_path, frame)
            return [True, file_name]
        return [False, "ERROR"]
    
    # Writes User Data
    def save_user_data(self):
        firstname = self.firstname.text().title()
        lastname = self.lastname.text().title()
        middleinitial = self.middlename.text().title()
        department = self.department.currentText()
        take_photo_state = self.take_photo()
        dthd.ProgramState.registeringpersonnel = False
        self.close()
        try:
            _user_name = f"{firstname} {middleinitial} {lastname}"
            take_photo_state = self.take_photo()
            _user_data = [f"{_user_name}", f"{department}", f"{take_photo_state[1]}"]
            if take_photo_state[0] == True:
                _file_path = dthd.load_user_data("Registration")
                _workbook = excel.load_workbook(_file_path)
                dthd.write_user_data(filepath=_file_path, workbook=_workbook, userdata=_user_data)
                return True
            self.error_dialog.show_error_message("Error Camera Cannot Take Picture")
            return False
        except:
            self.error_dialog.show_error_message("Error Could not save data")
            return False