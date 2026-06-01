
import socket
import threading
import signal
import sys
from datetime import datetime

server = None
ejecutando = True




def fecha_actual():
    return datetime.now().strftime("%Y.%m.%d %H:%M")




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




def cerrar(sig, frame):
    global ejecutando
    print("\nCTRL+C recibido. Cerrando sesión...")
    ejecutando = False
    if server:
        server.close()
    sys.exit(0)




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



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python receptor.py puerto")
        sys.exit(1)
    puerto = int(sys.argv[1])
    signal.signal(signal.SIGINT, cerrar)
    signal.signal(signal.SIGTERM, cerrar)
    iniciar_receptor(puerto)