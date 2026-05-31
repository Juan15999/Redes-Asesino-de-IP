import socket
import sys
import os

def recibir(client_socket, buf):
    while True:
        data = client_socket.recv(1024)
        buf += data.decode('utf-8')
        if "\r\n" in buf:
            break
    return buf

def enviar_archivo(file,header,elSocket):
    el_socket.send(header.encode('utf-8')) # Ver si lo de encode va.
    
    # Espera OK del servidor antes de enviar el archivo
    buf = recibir(elSocket, "")
    buf = buf.removesuffix("\r\n")
    print(buf)

    if buf != "OK":
        print("ERROR: El servidor rechazó la transferencia.")
        client_socket.close()
        sys.exit(1)
    
    tamEnviado = elSocket.sendfile(file)
    print(f"Archivo enviado: {enviados} bytes")
def abrir_archivo(path): #usando open, devuelve el tamanio del archivo
#def crearHeader(tipo,tamanio): # Ver si se tiene que poner el username 
