import socket
import hashlib
import os
import sys
import threading
import signal
import getpass
from datetime import datetime

LARGO_MAXIMO = 255

usuario = ""
nombre_completo = ""

server = None
ejecutando = True

def fecha_actual():
    return datetime.now().strftime("%Y.%m.%d %H:%M")

def recibir(client_socket, buf):
    while True:
        data = client_socket.recv(1024)
        buf += data.decode('utf-8')
        if "\r\n" in buf:
            break
    return buf

def enviar_datos(conexion, texto):
    conexion.sendall(texto.encode('utf-8'))

def enviar_archivo(file,header,elSocket):
    elSocket.send(header.encode('utf-8')) # Ver si lo de encode va.
    
    # Espera OK del servidor antes de enviar el archivo
    buf = recibir(elSocket, "")
    buf = buf.removesuffix("\r\n")
    print(buf)

    if buf != "OK": # el servidor no manda OK
        print("ERROR: El servidor rechazó la transferencia.")
        elSocket.close()
        sys.exit(1)
    
    tamEnviado = elSocket.sendfile(file)
    print(f"Archivo enviado: {tamEnviado} bytes")

def recibir_archivo(cliente, nombre_archivo, tamanio):
    try:
        with open(nombre_archivo, "wb") as archivo:
            recibidos = 0
            while recibidos < tamanio:
                datos = cliente.recv(min(4096, tamanio - recibidos))
                if not datos:
                    break
                archivo.write(datos)
                recibidos += len(datos)
        return True
    except Exception as e:
        print("Error:", e)
        return False


def convertir_a_md5(texto):
    return hashlib.md5(texto.encode()).hexdigest()


def autenticar(ip_servidor_auth, puerto_servidor_auth):
    global usuario, nombre_completo

    socket_auth = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    socket_auth.connect((ip_servidor_auth, puerto_servidor_auth))

    buf = ""
    buf = recibir(socket_auth, buf)

    usuario = input("Usuario: ")
    contrasena     = getpass.getpass("Clave: ")

    contrasena_md5 = convertir_a_md5(contrasena)
    mensaje_login  = usuario + "-" + contrasena_md5 + "\r\n"
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

def atender_cliente(cliente, direccion):
    try:
        encabezado = cliente.recv(1024).decode()
        if encabezado.startswith("MSG|"):
            partes = encabezado.split("|", 2)
            usuario = partes[1]
            mensaje = partes[2]
            print(
                f"[{fecha_actual()}] "
                f"{direccion[0]} "
                f"{usuario} dice: {mensaje}"
            )
        elif encabezado.startswith("FILE|"):
            partes = encabezado.split("|")
            usuario = partes[1]
            nombre_archivo = partes[2]
            tamanio = int(partes[3])
            ok = recibir_archivo(
                cliente,
                nombre_archivo,
                tamanio
            )
            if ok:
                print(
                    f"[{fecha_actual()}] "
                    f"{direccion[0]} "
                    f"<Recibido ./{nombre_archivo} de {usuario}>"
                )
            else:
                print(
                    f"[{fecha_actual()}] "
                    f"{direccion[0]} "
                    f"<Error Recibiendo Archivo de {usuario}>"
                )

    except Exception as e:
        print("Error atendiendo cliente:", e)
    finally:
        cliente.close()



def iniciar_receptor(puerto):
    global server
    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )
    server.bind(("", puerto))
    server.listen()
    print(f"Escuchando en puerto {puerto}")
    while ejecutando:
        try:
            cliente, direccion = server.accept()
            hilo = threading.Thread(
                target=atender_cliente,
                args=(cliente, direccion)
            )
            hilo.daemon = True
            hilo.start()
        except OSError:
            break


def cerrar(sig, frame):
    global ejecutando
    print("\nCTRL+C recibido. Cerrando sesión...")
    ejecutando = False
    if server:
        server.close()
    sys.exit(0)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python receptor.py puerto")
        sys.exit(1)
    puerto = int(sys.argv[1])
    ip_auth = sys.argv[2]
    puerto_auth = int(sys.argv[3])

    signal.signal(signal.SIGINT, cerrar)
    signal.signal(signal.SIGTERM, cerrar)

    if not autenticar(ip_auth, puerto_auth):
        print("Error al autenticarse.")
        sys.exit(1)

    
    iniciar_receptor(puerto)