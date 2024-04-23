from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, QDateTime
import cv2
import numpy as np

import os
import face_recognition
import library.data_handling as dthd
import library.datetime_safety as dtms

from library.student_regis_function import StudentRegisterDialog
from library.personnel_regis_function import PersonnelRegisterDialog
import library.error_handling as errh
import library.about_page as abpt

from gui.updatedMainGui import Ui_MainWindow

# Main Processes
class Display_MainWindow(QMainWindow):

    # Required Variables
    face_locations = []
    face_encodings = []
    face_names = []
    known_face_encodings = []
    known_face_names = []
    process_current_frame = True
    user_name = "Unknown"

    # Rectangle Color
    color_state = (0,0,255)

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.error_dialog = errh.ErrorDialog()
        self.about_page = abpt.AboutDialog()
        dthd.directory_safety("image_bank")
        dthd.directory_safety("attendance")

        self.paused = False

        self.capture = dthd.ProgramState.capture
        self.student_registration = StudentRegisterDialog()
        self.personnel_registration = PersonnelRegisterDialog()

        # Variables pointing to all the GUI objects required
        self.image_label = self.ui.cameraSurface
        self.display_greeting = self.ui.greeting
        self.display_username = self.ui.name
        self.display_userdepartment = self.ui.department
        self.display_time = self.ui.Time
        self.display_date = self.ui.Date
        self.return_old_greeting()
        
        # Button Actions
        self.ui.pushButton.clicked.connect(lambda: self.log_user("IN"))
        self.ui.pushButton_2.clicked.connect(lambda: self.log_user("OUT"))
        self.ui.actionOpen_Attendance_Folder.triggered.connect(lambda: self.menubutton_clicked("attendance"))
        self.ui.actionOpen_Student_Data.triggered.connect(lambda: self.menubutton_clicked("user_data.xlsx"))
        self.ui.actionOpen_Imagebank.triggered.connect(lambda: self.menubutton_clicked("image_bank"))
        self.ui.actionCameraOn.triggered.connect(lambda: self.toggle_pause(False))
        self.ui.actionCameraOff.triggered.connect(lambda: self.toggle_pause(True))
        self.ui.actionNew_Student.triggered.connect(lambda: self.register_user("Student"))
        self.ui.actionNew_Personnel.triggered.connect(lambda: self.register_user("Personnel"))
        self.ui.actionShowAbout.triggered.connect(lambda: self.about_page.show_about())

        # Prerequisites of the program
        self.encode_faces()
        self.user_data = dthd.load_user_data("Encoding")
        self.set_user_name("Unknown")

        # Timer required for live pause
        self.timer = self.startTimer(30)

    # Type Error Safety
    def set_user_name(self, varname):
        self.user_name = varname

    # Timer required for cameraSurface GUI object and Time Date QLabel Object
    # Timer runs at a rate of 30 miliseconds
    def timerEvent(self, event):
        # Time and Date QLabel
        current_time = QDateTime.currentDateTime()
        self.display_time.setText(current_time.toString('hh:mm:ss AP'))
        self.display_date.setText(current_time.toString('ddd, MMM dd, yyyy'))
        # Error safety
        try:
            if event.timerId() == self.timer and self.paused == False:
                ret, frame = self.capture.read()
                if ret:
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                    self.face_locations = face_recognition.face_locations(rgb_small_frame)
                    self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

                    self.face_names = []

                    # Runs through all encoded faces to find an accurate match
                    if self.face_encodings:
                        for face_encoding in self.face_encodings:
                            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)

                            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                            best_match_index = np.argmin(face_distances)

                            if matches[best_match_index]:
                                name = self.known_face_names[best_match_index]
                                confidence = dthd.face_confidence(face_distances[best_match_index])
                            else:
                                name = "Unknown"
                                confidence = "Unknown"

                            self.user_name = name
                            self.face_names.append(f'{name} ({confidence})')
                    else:
                        self.user_name = "Unknown"

                    for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):

                        # Returns image to full size
                        top *= 4
                        right *= 4
                        bottom *= 4
                        left *= 4

                        # Renders a rectangle over detected face
                        cv2.rectangle(frame, (left, top - 35), (right, bottom -35), self.color_state, 2)

                    # Connects to the GUI cameraSurface Object for displaying live pause
                    height, width, channels = frame.shape
                    bytes_per_line = channels * width
                    q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
                    pixmap = QPixmap.fromImage(q_image)
                    self.image_label.setPixmap(pixmap)
        except:
            self.return_error_greeting("Error: Could not Scan Face", " ", " ")

    # Encodes images in image_bank
    def encode_faces(self):
        program_dir = os.getcwd()
        object_path = os.path.join(program_dir, "image_bank\\")
        # Error safety
        self.toggle_pause(True)
        try:
            file_list = [f for f in os.listdir(object_path) if os.path.isfile(os.path.join(object_path, f))]
            if len(file_list) >= 1:
                for image in os.listdir(object_path):
                    face_image = face_recognition.load_image_file(f'{object_path}{image}')
                    face_encoding = face_recognition.face_encodings(face_image)[0]

                    self.known_face_encodings.append(face_encoding)
                    self.known_face_names.append(image)
                self.toggle_pause(False)
            else:
                self.error_dialog.show_error_message(f"Error Encoding Files. Images detected: {len(file_list)} \n Register Face then Restart Program.")
        except:
            self.return_error_greeting("Please Register a face first.", " ", "Then Restart Program.")
            self.error_dialog.show_error_message(f"Error Encoding Files. Images detected: 0 \n Register Face then Restart Program.")

    # Writes the data into a spreadsheet
    def log_user(self, state):
        if self.user_name == "Unknown":
            self.return_error_greeting("Error: Unknown Face Detected", " ", " ")
            QTimer.singleShot(5000, self.return_old_greeting)
        else:
            workbook = dthd.load_user_attendance("workbook")
            filepath = dthd.load_user_attendance("filepath")

            user_filepath = self.user_name.split(" ")
            user_filename = user_filepath[0].lower()

            try:
                save_state = dthd.write_user_attendance(workbook=workbook,
                    filepath=filepath,
                    user_data=self.user_data[user_filename],
                    time_log=dtms.get_current_time("str_time"),
                    user_status=state)
                if save_state == True:
                    if state == "OUT":
                        self.display_greeting.setText("Goodbye!")
                    else:
                        self.display_greeting.setText("Hello!")
                    self.display_username.setText(f"{self.user_data[user_filename][0]}")
                    self.display_userdepartment.setText(f"{self.user_data[user_filename][1]}")
                else:
                    self.return_error_greeting("Error: Attendance already logged.", " ", " ")
                    QTimer.singleShot(5000, self.return_old_greeting)
            except:
                self.error_dialog.show_error_message("Error could not log user.")
            QTimer.singleShot(5000, self.return_old_greeting)
        self.set_user_name("Unknown")

    def return_old_greeting(self):
        self.display_greeting.setText(" ")
        self.display_username.setText("Looking for a Face")
        self.display_userdepartment.setText(" ")

    def return_error_greeting(self, error_greeting, error_greeting_top, error_greeting_bottom):
        if self.paused == True:
            self.display_greeting.setText(" ")
            self.display_username.setText("Error: Camera Feed Offline")
            self.display_userdepartment.setText(" ")
        else:
            self.display_greeting.setText(f"{error_greeting_top}")
            self.display_username.setText(f"{error_greeting}")
            self.display_userdepartment.setText(f"{error_greeting_bottom}")
    
    def toggle_pause(self, camera_state):
        self.paused = camera_state

    def menubutton_clicked(self, object_name):
        self.toggle_pause(True)
        dthd.open_object(f"{object_name}")

    # Camera Safety
    # Opens corresponding GUIs
    def register_user(self, request_state):
        self.toggle_pause(True)
        if self.paused == True and request_state == "Student":
            dthd.ProgramState.registeringstudent = True
            self.student_registration.show()
        elif self.paused == True and request_state == "Personnel":
            dthd.ProgramState.registeringpersonnel = True
            self.personnel_registration.show()

    def closeEvent(self, event):
        self.capture.release()
        cv2.destroyAllWindows()