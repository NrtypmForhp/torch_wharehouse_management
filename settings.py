import sys, os

class SettingMainFunctions():
    def __init__(self):
        if getattr(sys, 'frozen', False): # Se viene avviato da un file eseguibile
            self.main_directory = os.path.dirname(sys.executable)
        elif __file__: # Se viene avviato direttamente dallo script
            self.main_directory = os.path.dirname(__file__)
        
        self.settings_directory = os.path.join(self.main_directory, "settings")
        self.messages_directory = os.path.join(self.main_directory, "messages")
        self.img_directory = os.path.join(self.settings_directory, "img")
    
    def load_settings(self) -> dict:
        settings_dict = {}
        if os.path.exists(os.path.join(self.settings_directory, "settings.txt")) == False:
            with open(os.path.join(self.settings_directory, "settings.txt"), "w") as settings_file:
                settings_file.write("database_connection_string: mongodb://localhost:27017/\n")
                settings_file.write("username: -\n")
                settings_file.write("password: -")
        with open(os.path.join(self.settings_directory, "settings.txt"), "r") as settings_file:
            for line in settings_file:
                settings_dict[line[:line.index(":")].strip()] = line[line.index(":")+1:].strip()
        return settings_dict
    
    def load_messages(self, file:str) -> dict:
        with open(os.path.join(self.messages_directory, f"{file}.txt"), "r") as message_file:
            messages = {}
            for message in message_file:
                messages[message[:message.index(":")]] = message[message.index(":")+1:].strip()
        return messages
    
    def load_stylesheet(self) -> str:
        with open(os.path.join(self.settings_directory, "style.txt"), "r") as style_file:
            style = style_file.read()
            style = style.replace("checkbox_checked_url", os.path.join(self.img_directory, "checkbox_checked_icon.png"))
            style = style.replace("checkbox_unchecked_url", os.path.join(self.img_directory, "checkbox_unchecked_icon.png"))
        return style