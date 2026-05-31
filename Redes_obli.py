#Leer entrada estándar, separar Destino del Mesanje #
import socket
import sys

Linea =  "192.168.33.15 Hola como estas!"
Partes = Linea.split(" ", 1)
Destino = Partes[0]
Mensaje = Partes[1]

if Destino == "*":
    ip = "255.255.255.255"
else: 
    ip = socket.gethostbyname(Destino)


#envio de mensaje#
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto(Mensaje.encode(), (ip, port))

        