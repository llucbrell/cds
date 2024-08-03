import os
import sys
import multiprocessing
import pystray
from PIL import Image
import webbrowser
import tkinter as tk
from tkinter import messagebox
import signal

app_port = 6996

def run_server():
    from app import app  # Importa el archivo que contiene la instancia de Flask
    app.run(port=app_port, use_reloader=False)

def stop_server(process):
    print("Stopping CDS Server...")
    os.kill(process.pid, signal.SIGTERM)  # Envía la señal SIGTERM al proceso del servidor

def create_image():
    ic_path = resource_path("static/images/cds_icon_5.png")
    return Image.open(ic_path)

def on_open_browser(icon, item):
    webbrowser.open(f'http://127.0.0.1:{app_port}')

def on_open_logs(icon, item):
    webbrowser.open('file:///' + os.path.abspath('app.log'))

def on_exit(icon, item):
    stop_server(server_process)
    icon.stop()

def setup(icon):
    icon.visible = True

def show_initial_dialog():
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal de Tkinter

    # Configurar el icono de la ventana principal
    icon_path = resource_path("static/images/cds_icon_5.ico")
    root.iconbitmap(icon_path)

    # Mostrar el mensaje de información
    messagebox.showinfo("Charlie Don't Surf", f"App Running on http://127.0.0.1:{app_port}")

def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, funciona para dev y PyInstaller"""
    try:
        # PyInstaller crea una carpeta temporal y almacena el camino en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    multiprocessing.freeze_support()

    semaphore = multiprocessing.Semaphore(1)
    
    if semaphore.acquire(block=False):
        server_process = multiprocessing.Process(target=run_server)
        server_process.start()

        show_initial_dialog()

        icon = pystray.Icon("flask_icon", create_image(), menu=pystray.Menu(
            pystray.MenuItem("Open on Browser", on_open_browser),
            pystray.MenuItem("Open logs", on_open_logs),
            pystray.MenuItem("Exit", on_exit)
        ),
        title="Charlie Don't Surf"
        )
        icon.run(setup)

        server_process.join()
    else:
        print("Another instance is already running.")
