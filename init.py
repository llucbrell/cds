import multiprocessing
import pystray
from PIL import Image, ImageDraw
import webbrowser
import tkinter as tk
from tkinter import messagebox
import time
import os
import signal

app_port = 6996

def run_server():
    import app  # Importa el archivo que contiene la instancia de Flask
    app.app.run(port=app_port, use_reloader=False)

def stop_server(process):
    print("Stopping CDS Server...")
    os.kill(process.pid, signal.SIGTERM)  # Envía la señal SIGTERM al proceso del servidor

def create_image():
    ic_path = os.path.abspath("./static/images/cds_icon_5.png")
    return Image.open(ic_path)  # Asegúrate de tener el archivo icon.png en el mismo directorio

def on_open_browser(icon, item):
    webbrowser.open('http://127.0.0.1:'+ str(app_port))

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
    icon_path = os.path.abspath("./static/images/cds_icon_5.ico")
    root.iconbitmap(icon_path)

    # Mostrar el mensaje de información
    messagebox.showinfo("Charlie Don't Surf", "App Running on http://127.0.0.1:" + str(app_port))


if __name__ == '__main__':
    # Iniciar el servidor Flask en un subproceso
    server_process = multiprocessing.Process(target=run_server)
    server_process.start()

    # Mostrar el diálogo inicial
    show_initial_dialog()

    # Configura y muestra el icono en la bandeja del sistema
    icon = pystray.Icon("flask_icon", create_image(), menu=pystray.Menu(
        pystray.MenuItem("Open on Browser", on_open_browser),
        pystray.MenuItem("Open logs", on_open_logs),
        pystray.MenuItem("Exit", on_exit)
    ),
    title="Charlie Don't Surf"
    )
    icon.run(setup)

    # Espera a que el proceso del servidor termine
    server_process.join()

