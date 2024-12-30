from PyQt6.QtWidgets import (QApplication, QWidget, QGridLayout, QVBoxLayout, QFrame, QLabel, QScrollArea, QPushButton, QComboBox, QLineEdit, QCheckBox,
                             QMessageBox)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QRunnable, QThreadPool, pyqtSlot
import sys, os, pymongo
from settings import SettingMainFunctions as SMF

# -*-* Signals *-*-

class Signals(QObject):
    login_status_signal = pyqtSignal(str)
    login_finished_signal = pyqtSignal(dict)

# -*-* Login Thread *-*-

class LoginThread(QRunnable):
    def __init__(self, mongodb_string:str, username:str, password:str):
        super().__init__()
        
        # Variabili iniziali
        
        if getattr(sys, 'frozen', False): # Se viene avviato da un file eseguibile
            self.main_directory = os.path.dirname(sys.executable)
        elif __file__: # Se viene avviato direttamente dallo script
            self.main_directory = os.path.dirname(__file__)

        self.settings_directory = os.path.join(self.main_directory, "settings")
        self.messages_directory = os.path.join(self.main_directory, "messages")
        self.img_directory = os.path.join(self.settings_directory, "img")
        
        self.mongodb_string = mongodb_string
        self.username = username
        self.password = password
        self.signal = Signals()
        
        # Caricamento messaggi
        self.messages = SMF.load_messages(self, "login")
    
    @pyqtSlot()
    def run(self):
        # Controllo connsessione al database
        self.signal.login_status_signal.emit(self.messages["database_connection_signal"])
        self.dbclient = pymongo.MongoClient(self.mongodb_string)
        try:
            self.dbclient.server_info()
        except:
            self.signal.login_status_signal.emit("")
            self.signal.login_finished_signal.emit({"error": self.messages["database_error"]})
            return
        
        # Controllo utente e password
        self.signal.login_status_signal.emit(self.messages["user_check_signal"])
        self.db = self.dbclient["torch"]
        col_users = self.db["users"]
        if col_users.count_documents({"username": self.username, "password": self.password}) == 0:
            self.signal.login_status_signal.emit("")
            self.signal.login_finished_signal.emit({"error": self.messages["user_error"]})
            return
        
        # Fine Thread
        self.signal.login_status_signal.emit("")
        return self.signal.login_finished_signal.emit({"error": "no"})

# -*-* Main *-*-

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Variabili iniziali
        
        if getattr(sys, 'frozen', False): # Se viene avviato da un file eseguibile
            self.main_directory = os.path.dirname(sys.executable)
        elif __file__: # Se viene avviato direttamente dallo script
            self.main_directory = os.path.dirname(__file__)

        self.settings_directory = os.path.join(self.main_directory, "settings")
        self.messages_directory = os.path.join(self.main_directory, "messages")
        self.img_directory = os.path.join(self.settings_directory, "img")
        
        self.sessions = [] # Sessioni aree
        
        # Caricamento messaggi
        self.messages = SMF.load_messages(self, "main")
        
        # Caricamento impostazioni
        self.settings = SMF.load_settings(self)
        
        # Impostazioni finestra
        
        self.setWindowTitle(self.messages["title"])
        self.setMinimumSize(700, 500)
        self.setWindowIcon(QIcon(os.path.join(self.img_directory, "Torch_icon.png")))
        self.lay = QGridLayout(self)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(0)
        
        # Stile finestra
        self.setStyleSheet(SMF.load_stylesheet(self))

        # Frame principali finestra
        self.frame_logo = QFrame(self)
        self.lay.addWidget(self.frame_logo, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.frame_logo_lay = QGridLayout(self.frame_logo)
        
        self.frame_options = QFrame(self)
        self.lay.addWidget(self.frame_options, 0, 1, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.frame_options_lay = QGridLayout(self.frame_options)
        
        self.frame_actions = QFrame(self)
        self.lay.addWidget(self.frame_actions, 1, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.frame_session = QFrame(self)
        self.lay.addWidget(self.frame_session, 1, 1, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.frame_session_lay = QGridLayout(self.frame_session)
        
        # Frame logo
        
        self.label_logo = QLabel(self)
        img_pixmap = QPixmap(os.path.join(self.img_directory, "Torch.png"))
        self.label_logo.setPixmap(img_pixmap)
        self.label_logo.resize(img_pixmap.width(), img_pixmap.height())
        self.frame_logo_lay.addWidget(self.label_logo, 0, 0, Qt.AlignmentFlag.AlignTop)
        
        # Frame Opzioni
        self.combobox_actual_session = QComboBox(self)
        self.combobox_actual_session.currentIndexChanged.connect(self.session_index_changed)
        self.frame_options_lay.addWidget(self.combobox_actual_session, 0, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        
        self.button_close_actual_session = QPushButton(self, text=self.messages["close"])
        self.button_close_actual_session.clicked.connect(self.close_actual_session)
        self.frame_options_lay.addWidget(self.button_close_actual_session, 0, 1, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        
        self.button_options = QPushButton(self, text=self.messages["options"])
        self.button_options.clicked.connect(self.start_options_session)
        self.frame_options_lay.addWidget(self.button_options, 0, 2, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        
        # -*-* Frame Sessione *-*-
        # Opzioni
        self.scrollarea_frame_session_options = QScrollArea(self.frame_session)
        
        self.frame_session_options = QFrame(self.frame_session)
        self.frame_session_lay.addWidget(self.frame_session_options, 0, 0, Qt.AlignmentFlag.AlignTop)
        self.frame_session_options_lay = QVBoxLayout(self.frame_session_options)
        
        self.scrollarea_frame_session_options.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollarea_frame_session_options.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollarea_frame_session_options.setWidgetResizable(True)
        self.scrollarea_frame_session_options.setWidget(self.frame_session_options)
        self.scrollarea_frame_session_options.hide()
        
        self.label_frame_session_options_options = QLabel(self.frame_session_options, text=self.messages["options"])
        self.label_frame_session_options_options.setAccessibleName("session_title")
        self.frame_session_options_lay.addWidget(self.label_frame_session_options_options, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.lineedit_frame_session_options_database_string = QLineEdit(self.frame_session_options)
        self.lineedit_frame_session_options_database_string.setPlaceholderText(self.messages["database_options_placeholder"])
        self.lineedit_frame_session_options_database_string.setText(self.settings["database_connection_string"])
        self.frame_session_options_lay.addWidget(self.lineedit_frame_session_options_database_string, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.lineedit_frame_session_options_username = QLineEdit(self.frame_session_options)
        self.lineedit_frame_session_options_username.setPlaceholderText(self.messages["username_options_placeholder"])
        if self.settings["username"] != "-": self.lineedit_frame_session_options_username.setText(self.settings["username"])
        self.frame_session_options_lay.addWidget(self.lineedit_frame_session_options_username, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.lineedit_frame_session_options_password = QLineEdit(self.frame_session_options)
        self.lineedit_frame_session_options_password.setPlaceholderText(self.messages["password_options_placeholder"])
        self.lineedit_frame_session_options_password.setEchoMode(QLineEdit.EchoMode.Password)
        if self.settings["password"] != "-": self.lineedit_frame_session_options_password.setText(self.settings["password"])
        self.frame_session_options_lay.addWidget(self.lineedit_frame_session_options_password, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.checkbox_frame_session_options_autologin = QCheckBox(self.frame_session_options, text=self.messages["auto_login"])
        self.frame_session_options_lay.addWidget(self.checkbox_frame_session_options_autologin, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.button_frame_session_options_save_options = QPushButton(self.frame_session_options, text=self.messages["save_options"])
        self.button_frame_session_options_save_options.clicked.connect(self.save_options)
        self.frame_session_options_lay.addWidget(self.button_frame_session_options_save_options, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.label_frame_session_options_response = QLabel(self)
        self.frame_session_options_lay.addWidget(self.label_frame_session_options_response, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Avvio threadpool
        
        self.pool = QThreadPool.globalInstance()
        
        # Controllo username e password
        
        if self.settings["username"] == "-" or self.settings["password"] == "-":
            self.button_options.click()
    
    def resizeEvent(self, a0):
        W_width = self.width()
        W_height = self.height()
        width_op = 300
        height_op = 150
        
        try:
            # Frame principali
            self.frame_logo.setFixedSize(width_op, height_op)
            self.frame_options.setFixedSize(W_width - width_op, height_op)
            self.frame_actions.setFixedSize(width_op, W_height - height_op)
            self.frame_session.setFixedSize(W_width - width_op, W_height - height_op)
            # Frame sessioni
            self.scrollarea_frame_session_options.setFixedSize(W_width - width_op, W_height - height_op)
            self.lineedit_frame_session_options_database_string.setFixedWidth(W_width - (width_op + 50))
            self.lineedit_frame_session_options_username.setFixedWidth(W_width - (width_op + 50))
            self.lineedit_frame_session_options_password.setFixedWidth(W_width - (width_op + 50))
        except AttributeError:
            pass
        return super().resizeEvent(a0)
    
    # Cambio index combobox sessioni
    
    def session_index_changed(self) -> None:
        if len(self.sessions) == 0: return
        session_index = self.combobox_actual_session.currentIndex()
        if self.sessions[session_index]["type"] == "options": self.replace_session_frame("options")
    
    # Chiusura sessione attuale
    
    def close_actual_session(self) -> None:
        if len(self.sessions) == 0: return
        session_index = self.combobox_actual_session.currentIndex()
        self.replace_session_frame()
        self.sessions.pop(session_index)
        self.combobox_actual_session.removeItem(session_index)
    
    # -*-* Sessioni *-*-
    
    # Sessione Opzioni
    def start_options_session(self) -> None:
        # Controllo se la sessione è già aperta
        for session in self.sessions:
            if session["type"] == "options": return self.combobox_actual_session.setCurrentIndex(self.sessions.index(session))
        self.sessions.append({"type": "options"})
        self.combobox_actual_session.addItem(self.messages["options"])
        self.combobox_actual_session.setCurrentText(self.messages["options"])
    
    def save_options(self) -> None:
        if self.lineedit_frame_session_options_database_string.text() == "" or self.lineedit_frame_session_options_username.text() == "" or self.lineedit_frame_session_options_password.text() == "":
            err_msg = QMessageBox(self)
            err_msg.setWindowTitle(self.messages["warning"])
            err_msg.setText(self.messages["options_field_warning_message"])
            return err_msg.exec()
        login = LoginThread(self.lineedit_frame_session_options_database_string.text(), self.lineedit_frame_session_options_username.text(), self.lineedit_frame_session_options_password.text())
        login.signal.login_finished_signal.connect(self.options_threadbreak)
        login.signal.login_status_signal.connect(self.options_status)
        self.pool.start(login)
        
    def options_status(self, response:str) -> None:
        self.label_frame_session_options_response.setText(response)
    
    def options_threadbreak(self, response:dict) -> None:
        if response["error"] != "no":
            err_msg = QMessageBox(self)
            err_msg.setWindowTitle(self.messages["warning"])
            err_msg.setText(response["error"])
            return err_msg.exec()
    
    # Pulizia e Impostazione Frame Sessione
    def replace_session_frame(self, activate:str="none") -> None:
        # Pulizia
        self.scrollarea_frame_session_options.hide()
        if activate == "options": self.scrollarea_frame_session_options.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()