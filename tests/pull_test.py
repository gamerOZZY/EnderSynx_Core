from pull import cargar_configuracion
import os

def crear_carpeta():

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    folder_name = "pull_test"
    new_folder = os.path.join(desktop_path, folder_name)
    os.makedirs(new_folder, exist_ok=True)
    print(f"Carpeta creada en: {new_folder}")

def test1():
    pass