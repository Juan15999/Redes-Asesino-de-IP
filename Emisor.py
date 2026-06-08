import socket
import sys
from Lista_usuarios import *
from usuarios import *
from datetime import datetime

def detect_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip    



ip_emisor = detect_local_ip()

def start_emisor(port, usuario_obj=None, ip_emisor=None):
    if ip_emisor is None:
        ip_emisor = detect_local_ip()
    """Inicia el emisor UDP en el puerto `port`."""
    # Crea el socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Determinar usuario
    if usuario_obj is None:
        usuario = input("Ingrese su nombre de usuario: ")
    else:
        # si viene un objeto Usuario, obtener el nombre; si es str, usarlo
        if hasattr(usuario_obj, 'get_usuario'):
            usuario = usuario_obj.get_usuario()
        else:
            usuario = str(usuario_obj)

    while True:
        try:
            linea = input()
        except EOFError:
            break

        partes = linea.split(" ", 1)
        destino = partes[0]
        if len(partes) < 2:                     # se fija si hay 2 argumentos, sino vuelve a pedir
            print("Formato invalido, tiene que ser |Destino| |Mensaje|")
            continue
        mensaje = partes[1]

        # resolver ip
        if destino == "*":                      # Se fija si es broadcast
            ip = "255.255.255.255"
        else:
            try:
                ip = socket.gethostbyname(destino)
            except socket.gaierror:
                print(f"No se pudo resolver destino: {destino}")
                continue

        if mensaje.startswith("&file"):
            path = mensaje.split(" ", 1)[1]     # te da solo el ./
            try:
                with open(path, "rb") as f:
                    datos = f.read()

                nombre_archivo = path.split("/")[-1]    # extrae el nombre del archivo
                encabezado = f"{ip_emisor} {usuario} &file {nombre_archivo}".encode()
                sock.sendto(encabezado, (ip, port))
                sock.sendto(datos, (ip, port))          # devuelve archivo
            except FileNotFoundError:
                print(f"Error: no se encontró el archivo {path}")

        else:
            formato_del_mensaje = f"{ip_emisor} {usuario} dice: {mensaje}"      # seteo el tipo de mensaje
            sock.sendto(formato_del_mensaje.encode(), (ip, port))               # envia mensaje


    if __name__ == "__main__":
        if len(sys.argv) < 2:
            print("Uso: python Emisor.py <puerto>")
            sys.exit(1)
        port = int(sys.argv[1])
        start_emisor(port)
