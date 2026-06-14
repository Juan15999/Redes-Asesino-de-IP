#!/usr/bin/env python3

# Integrantes:
# - Juan Cabot 5049456-2
# - Adrian Pique 4896224-9
# - Alejo Focco 5492450-9
# - Bruno Borges 5395353-1
# - Federico Gianfagna 5488775-1

import socket
import hashlib
import os
import sys
import threading
import signal
import getpass
from datetime import datetime

LARGO_MAXIMO    = 255
nombre_usuario  = ""
nombre_completo = ""
ejecutando      = True
server_tcp      = None

def fecha_actual():
    return datetime.now().strftime("%Y.%m.%d %H:%M")

def recibir(client_socket, buf):
    while True:
        data = client_socket.recv(1)
        buf += data.decode('utf-8')
        if "\r\n" in buf:
            break
    return buf

def convertir_a_md5(texto):
    return hashlib.md5(texto.encode()).hexdigest()

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

def autenticar(ip_servidor_auth, puerto_servidor_auth):
    global nombre_usuario, nombre_completo

    socket_auth = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_auth.connect((ip_servidor_auth, puerto_servidor_auth))

    buf = ""
    buf = recibir(socket_auth, buf)

    nombre_usuario = input("Usuario: ")
    contrasena     = getpass.getpass("Clave: ")

    contrasena_md5 = convertir_a_md5(contrasena)
    mensaje_login  = nombre_usuario + "-" + contrasena_md5 + "\r\n"
    socket_auth.send(mensaje_login.encode('utf-8'))

    buf = ""
    buf = recibir(socket_auth, buf)
    buf = buf.removesuffix("\r\n")

    if buf == "SI":
        buf2 = ""
        buf2 = recibir(socket_auth, buf2)
        nombre_completo = buf2.removesuffix("\r\n")
        print("Bienvenido " + nombre_completo)
        socket_auth.close()
        return True
    else:
        print("Usuario o contrasena incorrectos.")
        socket_auth.close()
        return False

def start_receptor_udp(puerto):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", puerto))

    while ejecutando:
        try:
            data, _ = sock.recvfrom(65535)
            mensaje = data.decode(errors="ignore")
            print("[" + fecha_actual() + "] " + mensaje)
        except OSError:
            break

    sock.close()

def atender_tcp(cliente, direccion):
    try:
        # Leer encabezado byte a byte hasta encontrar \r\n
        encabezado = b""
        while not encabezado.endswith(b"\r\n"):
            byte = cliente.recv(1)
            if not byte:
                break
            encabezado += byte

        partes         = encabezado.decode().strip().split("|")
        # Formato: FILE|usuario|nombre_archivo|tamanio
        usuario        = partes[1]
        nombre_archivo = partes[2]
        tamanio        = int(partes[3])

        with open(nombre_archivo, "wb") as f:
            recibidos = 0
            while recibidos < tamanio:
                chunk = cliente.recv(min(4096, tamanio - recibidos))
                if not chunk:
                    break
                f.write(chunk)
                recibidos += len(chunk)

        print("[" + fecha_actual() + "] " + direccion[0] +
            " <Recibido ./" + nombre_archivo + " de " + usuario + ">")

    except Exception as e:
        print("[" + fecha_actual() + "] " + direccion[0] +
            " <Error Recibiendo Archivo de " + (partes[1] if len(partes) > 1 else "?") + ">")
    finally:
        cliente.close()

def start_receptor_tcp(puerto):
    global server_tcp
    server_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_tcp.bind(("", puerto))
    server_tcp.listen()

    while ejecutando:
        try:
            cliente, direccion = server_tcp.accept()
            hilo = threading.Thread(target=atender_tcp, args=(cliente, direccion))
            hilo.daemon = True
            hilo.start()
        except OSError:
            break

def start_emisor(puerto):
    ip_emisor = detect_local_ip()

    sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while ejecutando:
        try:
            linea = input()
        except (EOFError, KeyboardInterrupt):
            break

        partes = linea.split(" ", 1)
        if len(partes) < 2:
            print("Formato invalido. Tiene que ser: <destino> <mensaje>")
            continue

        destino = partes[0]
        mensaje = partes[1]

        if destino == "*":
            ip = "255.255.255.255"
        else:
            try:
                ip = socket.gethostbyname(destino)
            except socket.gaierror:
                print("Error: no se pudo resolver " + destino)
                continue

        if mensaje.startswith("&file"):
            # Envio de archivo por TCP
            partes_file    = mensaje.split(" ", 1)
            if len(partes_file) < 2:
                print("Formato invalido. Tiene que ser: <destino> &file <path>")
                continue
            path           = partes_file[1]
            nombre_archivo = path.split("/")[-1]

            if destino == "*":
                print("Error: no se puede enviar archivos por broadcast.")
                continue

            try:
                tamanio = os.path.getsize(path)
            except FileNotFoundError:
                print("Error: no se encontro el archivo " + path)
                continue

            try:
                sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock_tcp.connect((ip, puerto))

                encabezado = "FILE|" + nombre_usuario + "|" + nombre_archivo + "|" + str(tamanio) + "\r\n"
                sock_tcp.send(encabezado.encode())

                with open(path, "rb") as f:
                    sock_tcp.sendfile(f)

                sock_tcp.close()
            except Exception as e:
                print("Error enviando archivo: " + str(e))

        else:
            # Envio de mensaje de texto por UDP
            formato_mensaje = ip_emisor + " " + nombre_usuario + " dice: " + mensaje[:LARGO_MAXIMO]
            sock_udp.sendto(formato_mensaje.encode(), (ip, puerto))

    sock_udp.close()

# termina cuando pone CTRL + C
def cerrar(_, __):
    global ejecutando
    print("\nCTRL + C Recibido.... Cerrando Sesion")
    ejecutando = False
    if server_tcp:
        server_tcp.close()
    sys.exit(0)

def main():
    if len(sys.argv) != 4:
        print("Uso: python3 mensajeria.py port ipAuth portAuth")
        sys.exit(1)

    puerto_local = int(sys.argv[1])
    ip_auth      = sys.argv[2]
    puerto_auth  = int(sys.argv[3])

    signal.signal(signal.SIGINT,  cerrar)
    signal.signal(signal.SIGTERM, cerrar)

    if not autenticar(ip_auth, puerto_auth):
        sys.exit(1)

    # Receptor UDP en hilo separado
    hilo_udp = threading.Thread(target=start_receptor_udp, args=(puerto_local,))
    hilo_udp.daemon = True
    hilo_udp.start()

    # Receptor TCP en hilo separado
    hilo_tcp = threading.Thread(target=start_receptor_tcp, args=(puerto_local,))
    hilo_tcp.daemon = True
    hilo_tcp.start()

    # Emisor en hilo principal, cuando este termina se cierran los receptores
    start_emisor(puerto_local)

if __name__ == "__main__":
    main()