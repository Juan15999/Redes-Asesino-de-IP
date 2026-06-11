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
server          = None

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
    # Obtiene la IP local de esta maquina
    # Se conecta a 8.8.8.8 sin mandar nada y lee desde que IP salio
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

    # Crear y conectar el socket al servidor de autenticacion
    socket_auth = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_auth.connect((ip_servidor_auth, puerto_servidor_auth))

    # Leer el saludo del servidor (obligatorio para que el protocolo funcione)
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

def start_receptor(puerto):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", puerto))

    while ejecutando:
        try:
            data, addr = sock.recvfrom(65535)

            mensaje = data.decode(errors="ignore")
            if "&file" in mensaje:
                partes         = mensaje.split(" ")
                ip_emisor      = partes[0]
                usuario        = partes[1]
                nombre_archivo = partes[3]

                datos_archivo, _ = sock.recvfrom(65535)
                try:
                    with open(nombre_archivo, "wb") as f:
                        f.write(datos_archivo)
                    print("[" + fecha_actual() + "] " + ip_emisor +
                        " <Recibido ./" + nombre_archivo + " de " + usuario + ">")
                except Exception:
                    print("[" + fecha_actual() + "] " + ip_emisor +
                        " <Error Recibiendo Archivo de " + usuario + ">")
            else:
                print("[" + fecha_actual() + "] " + mensaje)

        except OSError:
            break

    sock.close()

def start_emisor(puerto):
    ip_emisor = detect_local_ip()

    # pura ia esto, es para mandar mensajes a cualquier IP sin importar si es local o no, y para mandar broadcast
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

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

        # esto hay que mirarlo bien, no se si es asi
        if destino == "*":
            ip = "255.255.255.255"
        else:
            try:
                ip = socket.gethostbyname(destino)
            except socket.gaierror:
                print("Error: no se pudo resolver " + destino)
                continue

        # si manda mensaje con &file manda un archivo, sino es mensaje
        if mensaje.startswith("&file"):
            path           = mensaje.split(" ", 1)[1]
            nombre_archivo = path.split("/")[-1]
            try:
                with open(path, "rb") as f:
                    datos = f.read()
                # mandamos el encabezado
                encabezado = (ip_emisor + " " + nombre_usuario + " &file " + nombre_archivo).encode()
                sock.sendto(encabezado, (ip, puerto))
                # mandamos el contenido del archivo
                sock.sendto(datos, (ip, puerto))
            except FileNotFoundError:
                print("Error: no se encontro el archivo " + path)
        else:
            formato_mensaje = ip_emisor + " " + nombre_usuario + " dice: " + mensaje[:LARGO_MAXIMO]
            sock.sendto(formato_mensaje.encode(), (ip, puerto))

    sock.close()


# control + c
def cerrar(sig, frame):
    global ejecutando
    print("\nCTRL + C Recibido.... Cerrando Sesion")
    ejecutando = False
    if server:
        server.close()
    sys.exit(0)



if len(sys.argv) != 4:
    print("Uso: python3 mensajeria.py port ipAuth portAuth")
    sys.exit(1)

puerto_local = int(sys.argv[1])
ip_auth      = sys.argv[2]
puerto_auth  = int(sys.argv[3])

# Registrar senales
signal.signal(signal.SIGINT,  cerrar)
signal.signal(signal.SIGTERM, cerrar)

if not autenticar(ip_auth, puerto_auth):
    sys.exit(1)

hilo_receptor = threading.Thread(target=start_receptor, args=(puerto_local,))
hilo_receptor.daemon = True
hilo_receptor.start()

# Emisor en el hilo principal
start_emisor(puerto_local)