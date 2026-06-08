import socket
import sys
from datetime import datetime
import hashlib
from Lista_usuarios import *    
import usuarios
import threading
import signal 


# Largo máximo esperado para los mensajes (en bytes)
MAX_LEN = 255


def formatear_fecha_hora():
    return datetime.now().strftime("%Y.%m.%d %H:%M")


def start_receptor(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", port))
    print(f"Receptor escuchando en puerto {port}")

    try:
        while True:
            data, addr = sock.recvfrom(65535)

            # Truncar si excede el largo máximo definido
            if len(data) > MAX_LEN:
                print(f"[{formatear_fecha_hora()}] {addr[0]}: Mensaje demasiado largo ({len(data)} bytes), se truncará a {MAX_LEN} bytes")
                data = data[:MAX_LEN]

            texto = data.decode(errors="replace").strip()

            # Se espera el formato: "<ip_emisor> <usuario> dice: <mensaje>"
            partes = texto.split(" ", 2)
            if len(partes) >= 3:
                ip_emisor = partes[0]
                usuario = partes[1]
                resto = partes[2]
                # resto debería empezar con "dice: "
                if resto.startswith("dice: "):
                    mensaje = resto[len("dice: "):]
                else:
                    mensaje = resto

                print(f"[{formatear_fecha_hora()}] {ip_emisor} {usuario}: {mensaje}")
            else:
                # Formato inesperado: imprimimos la línea tal cual junto con origen
                print(f"[{formatear_fecha_hora()}] {addr[0]}: {texto}")

    except KeyboardInterrupt:
        print("\nReceptor interrumpido por el usuario. Saliendo...")
    finally:
        sock.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python Receptor.py <puerto>")
        sys.exit(1)
    puerto = int(sys.argv[1])
    start_receptor(puerto)
import socket
import sys
import os

def start_receptor(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", port))
    print(f"Receptor escuchando en puerto {port}")

    while True:
        data, addr = sock.recvfrom(65535)
        mensaje = data.decode(errors="ignore")

        if "&file" in mensaje:
            partes = mensaje.split(" ")
            nombre_archivo = partes[-1]
            print(f"Recibiendo archivo {nombre_archivo} de {addr[0]}")

            datos_archivo, _ = sock.recvfrom(65535)
            with open(nombre_archivo, "wb") as f:
                f.write(datos_archivo)

            print(f"Archivo guardado: {nombre_archivo}")
        else:
            print(f"{addr[0]}: {mensaje}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python Receptor.py <puerto>")
        sys.exit(1)
    start_receptor(int(sys.argv[1]))