import sys, os

# Variabili globali
main_directory = ""
        
if getattr(sys, 'frozen', False): # Se viene avviato da un file eseguibile
    main_directory = os.path.dirname(sys.executable)
elif __file__: # Se viene avviato direttamente dallo script
    main_directory = os.path.dirname(__file__)
settings_directory = os.path.join(main_directory, "settings")
messages_directory = os.path.join(main_directory, "messages")
img_directory = os.path.join(settings_directory, "img")
    
def load_settings() -> dict:
    settings_dict = {}
    if os.path.exists(os.path.join(settings_directory, "settings.txt")) == False:
        with open(os.path.join(settings_directory, "settings.txt"), "w") as settings_file:
            settings_file.write("database_connection_string: mongodb://localhost:27017/\n")
            settings_file.write("username: -\n")
            settings_file.write("password: -")
    with open(os.path.join(settings_directory, "settings.txt"), "r") as settings_file:
        for line in settings_file:
            settings_dict[line[:line.index(":")].strip()] = line[line.index(":")+1:].strip()
    return settings_dict

def update_settings(mongodb_string:str, username:str, password:str) -> None:
    with open(os.path.join(settings_directory, "settings.txt"), "w") as settings_file:
        settings_file.write(f"database_connection_string: {mongodb_string}\n")
        settings_file.write(f"username: {username}\n")
        settings_file.write(f"password: {password}")
    
def load_messages(file:str) -> dict:
    with open(os.path.join(messages_directory, f"{file}.txt"), "r") as message_file:
        messages = {}
        for message in message_file:
            messages[message[:message.index(":")]] = message[message.index(":")+1:].strip()
    return messages
    
def load_stylesheet() -> str:
    with open(os.path.join(settings_directory, "style.txt"), "r") as style_file:
        style = style_file.read()
        style = style.replace("checkbox_checked_url", os.path.join(img_directory, "checkbox_checked_icon.png"))
        style = style.replace("checkbox_unchecked_url", os.path.join(img_directory, "checkbox_unchecked_icon.png"))
    return style